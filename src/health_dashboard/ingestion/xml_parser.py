from __future__ import annotations

import csv
import io
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from health_dashboard import CSVSchemaError, IngestionReport
from health_dashboard.config import (
    HR_VALID_RANGE,
    LOCAL_TZ,
    OOM_HR_ROW_LIMIT,
    OOM_MIN_USABLE_ROWS,
)
from health_dashboard.ingestion.stage_mapping import map_stages


_HK_HEART_RATE = "HKQuantityTypeIdentifierHeartRate"
_HK_SLEEP_ANALYSIS = "HKCategoryTypeIdentifierSleepAnalysis"

_HR_FIELDS = ("sourceName", "unit", "value", "startDate")
_SLEEP_FIELDS = ("sourceName", "value", "startDate", "endDate")

STREAMLIT_DEFAULT_UPLOAD_LIMIT_MB = 200
RECOMMENDED_MAX_UPLOAD_MB = 1024


def _parse_apple_datetime(raw: str) -> "pd.Timestamp | None":
    try:
        return pd.Timestamp(raw).tz_convert("UTC")
    except Exception:
        try:
            return pd.to_datetime(raw, utc=True)
        except Exception:
            return None


def _single_pass_stream(
    xml_source: "str | io.BytesIO",
) -> tuple[io.StringIO, io.StringIO, int, int]:
    hr_buf = io.StringIO()
    sleep_buf = io.StringIO()

    hr_writer = csv.DictWriter(
        hr_buf,
        fieldnames=list(_HR_FIELDS),
        extrasaction="ignore",
    )
    sleep_writer = csv.DictWriter(
        sleep_buf,
        fieldnames=list(_SLEEP_FIELDS),
        extrasaction="ignore",
    )

    hr_writer.writeheader()
    sleep_writer.writeheader()

    hr_count = 0
    sleep_count = 0
    root = None

    try:
        context = ET.iterparse(xml_source, events=("start", "end"))

        for event, elem in context:
            if event == "start" and root is None:
                root = elem
                continue

            if event == "end" and elem.tag == "Record":
                record_type = elem.attrib.get("type", "")

                if record_type == _HK_HEART_RATE:
                    hr_writer.writerow(elem.attrib)
                    hr_count += 1
                elif record_type == _HK_SLEEP_ANALYSIS:
                    sleep_writer.writerow(elem.attrib)
                    sleep_count += 1

                elem.clear()

                if root is not None:
                    del root[:]

    except ET.ParseError as exc:
        raise CSVSchemaError(
            f"XML súbor je poškodený alebo má neplatný formát: {exc}\n"
            "Uistite sa, že nahrávate originálny súbor export.xml z Apple Health."
        ) from exc

    hr_buf.seek(0)
    sleep_buf.seek(0)

    return hr_buf, sleep_buf, hr_count, sleep_count


def save_upload_to_tempfile(uploaded_file) -> str:
    suffix = Path(getattr(uploaded_file, "name", "export.xml")).suffix or ".xml"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)

    try:
        with os.fdopen(fd, "wb") as f:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)

            while True:
                chunk = uploaded_file.read(8 * 1024 * 1024)

                if not chunk:
                    break

                f.write(chunk)

    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        raise

    return tmp_path


def _build_hr_dataframe(
    hr_csv_buf: io.StringIO,
    local_tz: str,
) -> tuple[pd.DataFrame, int, int, int, bool, int]:
    df = pd.read_csv(hr_csv_buf)
    rows_read = len(df)

    df["source_raw"] = (
        df["sourceName"].fillna("unknown")
        if "sourceName" in df.columns
        else "unknown"
    )
    df["unit"] = (
        df["unit"].fillna("count/min")
        if "unit" in df.columns
        else "count/min"
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["ts_utc"] = df["startDate"].apply(_parse_apple_datetime)

    invalid_mask = df["ts_utc"].isna() | df["value"].isna()
    rows_dropped_invalid = int(invalid_mask.sum())
    df = df[~invalid_mask].copy()

    hr_min, hr_max = HR_VALID_RANGE
    oor_mask = (df["value"] <= hr_min) | (df["value"] > hr_max)
    rows_dropped_oor = int(oor_mask.sum())
    df = df[~oor_mask].copy()

    df["ts_local"] = df["ts_utc"].dt.tz_convert(local_tz)
    df = df.sort_values("ts_utc").reset_index(drop=True)
    df["id"] = df.index + 1

    original_row_count = len(df)
    was_downsampled = False

    if len(df) > OOM_HR_ROW_LIMIT:
        step = max(1, len(df) // OOM_HR_ROW_LIMIT)
        df = df.iloc[::step].head(OOM_HR_ROW_LIMIT).reset_index(drop=True)
        was_downsampled = True

        if len(df) < OOM_MIN_USABLE_ROWS:
            from health_dashboard import OOMGuardError

            raise OOMGuardError(
                f"HR dataset je príliš veľký. Po downsamplingu na "
                f"{OOM_HR_ROW_LIMIT} záznamov je výsledok príliš malý "
                "na analýzu. Skúste exportovať kratšie časové obdobie."
            )

    df = df[["id", "value", "unit", "ts_utc", "ts_local", "source_raw"]].copy()

    return (
        df,
        rows_read,
        rows_dropped_invalid,
        rows_dropped_oor,
        was_downsampled,
        original_row_count,
    )


def _build_sleep_dataframe(
    sleep_csv_buf: io.StringIO,
    local_tz: str,
) -> tuple[pd.DataFrame, int, int, int]:
    df = pd.read_csv(sleep_csv_buf)
    rows_read = len(df)

    df["source_raw"] = (
        df["sourceName"].fillna("unknown")
        if "sourceName" in df.columns
        else "unknown"
    )

    df["start_utc"] = df["startDate"].apply(_parse_apple_datetime)
    df["end_utc"] = df["endDate"].apply(_parse_apple_datetime)

    invalid_mask = df["start_utc"].isna() | df["end_utc"].isna()
    invalid_range_mask = df["end_utc"] <= df["start_utc"]
    rows_dropped_invalid = int((invalid_mask | invalid_range_mask).sum())
    df = df[~(invalid_mask | invalid_range_mask)].copy()

    df["start_local"] = df["start_utc"].dt.tz_convert(local_tz)
    df["end_local"] = df["end_utc"].dt.tz_convert(local_tz)
    df["duration_s"] = (df["end_utc"] - df["start_utc"]).dt.total_seconds()

    df["raw_value"] = df["value"]
    df = map_stages(df, raw_col="value")
    unknown_stage_count = int((df["stage"] == "Other").sum())

    df = df.sort_values("start_utc").reset_index(drop=True)
    df["id"] = df.index + 1

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
            "source_raw",
        ]
    ].copy()

    return df, rows_read, rows_dropped_invalid, unknown_stage_count


def parse_apple_health_xml(
    xml_source: "str | io.BytesIO",
    local_tz: str = LOCAL_TZ,
) -> tuple[
    "pd.DataFrame | None",
    "pd.DataFrame | None",
    "IngestionReport | None",
    "IngestionReport | None",
]:
    hr_buf, sleep_buf, hr_count, sleep_count = _single_pass_stream(xml_source)

    hr_df = hr_report = None
    sleep_df = sleep_report = None

    if hr_count > 0:
        (
            hr_df,
            hr_rows_read,
            hr_dropped_invalid,
            hr_dropped_oor,
            hr_downsampled,
            hr_original,
        ) = _build_hr_dataframe(hr_buf, local_tz)

        hr_report = IngestionReport(
            filename="export.xml (heart rate)",
            rows_read=hr_rows_read,
            rows_dropped_invalid=hr_dropped_invalid,
            rows_dropped_out_of_range=hr_dropped_oor,
            unknown_stage_count=0,
            was_downsampled=hr_downsampled,
            original_row_count=hr_original if hr_downsampled else 0,
        )

    if sleep_count > 0:
        (
            sleep_df,
            sleep_rows_read,
            sleep_dropped_invalid,
            sleep_unknown_stages,
        ) = _build_sleep_dataframe(sleep_buf, local_tz)

        sleep_report = IngestionReport(
            filename="export.xml (sleep)",
            rows_read=sleep_rows_read,
            rows_dropped_invalid=sleep_dropped_invalid,
            rows_dropped_out_of_range=0,
            unknown_stage_count=sleep_unknown_stages,
            was_downsampled=False,
            original_row_count=0,
        )

    return hr_df, sleep_df, hr_report, sleep_report


def extract_heart_rate_from_xml(
    buf: "io.BytesIO",
    local_tz: str = LOCAL_TZ,
) -> tuple[pd.DataFrame, IngestionReport]:
    hr_df, _, hr_report, _ = parse_apple_health_xml(buf, local_tz)

    if hr_df is None:
        raise CSVSchemaError(
            "V XML neboli nájdené žiadne záznamy srdcovej frekvencie. "
            "Overte, že export obsahuje dáta 'Heart Rate' z Apple Health."
        )

    return hr_df, hr_report


def extract_sleep_from_xml(
    buf: "io.BytesIO",
    local_tz: str = LOCAL_TZ,
) -> tuple[pd.DataFrame, IngestionReport]:
    _, sleep_df, _, sleep_report = parse_apple_health_xml(buf, local_tz)

    if sleep_df is None:
        raise CSVSchemaError(
            "V XML neboli nájdené žiadne záznamy analýzy spánku. "
            "Overte, že export obsahuje dáta 'Sleep' z Apple Health."
        )

    return sleep_df, sleep_report