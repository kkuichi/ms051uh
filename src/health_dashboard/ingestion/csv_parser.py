from io import BytesIO

import pandas as pd

from health_dashboard import (
    CSVSchemaError,
    IngestionReport,
    OOMGuardError,
)
from health_dashboard.config import (
    HR_VALID_RANGE,
    LOCAL_TZ,
    OOM_HR_ROW_LIMIT,
    OOM_MIN_USABLE_ROWS,
)
from health_dashboard.ingestion.stage_mapping import map_stages
from health_dashboard.ingestion.validator import (
    validate_hr_schema,
    validate_sleep_schema,
)


def parse_heart_rate(
    buf: BytesIO,
    filename: str = "",
    local_tz: str = LOCAL_TZ,
) -> tuple[pd.DataFrame, IngestionReport]:
    buf.seek(0)

    df = pd.read_csv(buf, sep=";", encoding="utf-8-sig")

    validate_hr_schema(df)

    rows_read = len(df)

    df.columns = df.columns.str.lower()

    try:
        df["ts_utc"] = pd.to_datetime(
            df["startdate"],
            format="%Y-%m-%d %H:%M:%S %z",
            utc=True,
            errors="coerce",
        )
    except Exception as e:
        raise CSVSchemaError(f"Failed to parse startDate column: {str(e)}")

    invalid_mask = df["ts_utc"].isna()
    rows_dropped_invalid = invalid_mask.sum()
    df = df[~invalid_mask].copy()

    hr_min, hr_max = HR_VALID_RANGE

    out_of_range_mask = (
        (df["value"] <= hr_min)
        | (df["value"] > hr_max)
    )

    rows_dropped_out_of_range = out_of_range_mask.sum()
    df = df[~out_of_range_mask].copy()

    df["ts_local"] = df["ts_utc"].dt.tz_convert(local_tz)

    df = df[
        ["id", "value", "unit", "ts_utc", "ts_local"]
    ].copy()

    df = df.sort_values("ts_utc").reset_index(drop=True)

    original_row_count = len(df)
    was_downsampled = False

    if len(df) > OOM_HR_ROW_LIMIT:
        step = max(1, len(df) // OOM_HR_ROW_LIMIT)

        df = (
            df.iloc[::step]
            .head(OOM_HR_ROW_LIMIT)
            .reset_index(drop=True)
        )

        was_downsampled = True

        if len(df) < OOM_MIN_USABLE_ROWS:
            raise OOMGuardError(
                f"Dataset too large; after downsampling to "
                f"{OOM_HR_ROW_LIMIT} rows "
                f"(from {original_row_count}), result is unusable. "
                f"Minimum {OOM_MIN_USABLE_ROWS} rows required."
            )

    report = IngestionReport(
        filename=filename,
        rows_read=rows_read,
        rows_dropped_invalid=rows_dropped_invalid,
        rows_dropped_out_of_range=rows_dropped_out_of_range,
        unknown_stage_count=0,
        was_downsampled=was_downsampled,
        original_row_count=(
            original_row_count if was_downsampled else 0
        ),
    )

    return df, report


def parse_sleep(
    buf: BytesIO,
    filename: str = "",
    local_tz: str = LOCAL_TZ,
) -> tuple[pd.DataFrame, IngestionReport]:
    buf.seek(0)

    df = pd.read_csv(buf, sep=";", encoding="utf-8-sig")

    validate_sleep_schema(df)

    rows_read = len(df)

    df.columns = df.columns.str.lower()

    try:
        df["start_utc"] = pd.to_datetime(
            df["startdate"],
            format="%Y-%m-%d %H:%M:%S %z",
            utc=True,
            errors="coerce",
        )

        df["end_utc"] = pd.to_datetime(
            df["enddate"],
            format="%Y-%m-%d %H:%M:%S %z",
            utc=True,
            errors="coerce",
        )

    except Exception as e:
        raise CSVSchemaError(
            f"Failed to parse date columns: {str(e)}"
        )

    invalid_mask = (
        df["start_utc"].isna()
        | df["end_utc"].isna()
    )

    invalid_range_mask = (
        df["end_utc"] <= df["start_utc"]
    )

    rows_dropped_invalid = (
        invalid_mask | invalid_range_mask
    ).sum()

    df = df[
        ~(invalid_mask | invalid_range_mask)
    ].copy()

    df["start_local"] = (
        df["start_utc"].dt.tz_convert(local_tz)
    )

    df["end_local"] = (
        df["end_utc"].dt.tz_convert(local_tz)
    )

    df["duration_s"] = (
        df["end_utc"] - df["start_utc"]
    ).dt.total_seconds()

    df["raw_value"] = df["value"]

    df = map_stages(df, raw_col="value")

    unknown_stage_count = (
        df["stage"] == "Other"
    ).sum()

    df = df[
        [
            "id",
            "raw_value",
            "stage",
            "start_utc",
            "end_utc",
            "start_local",
            "end_local",
            "duration_s",
        ]
    ].copy()

    df = (
        df.sort_values("start_utc")
        .reset_index(drop=True)
    )

    report = IngestionReport(
        filename=filename,
        rows_read=rows_read,
        rows_dropped_invalid=rows_dropped_invalid,
        rows_dropped_out_of_range=0,
        unknown_stage_count=unknown_stage_count,
        was_downsampled=False,
        original_row_count=0,
    )

    return df, report