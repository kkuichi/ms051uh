from __future__ import annotations

import pandas as pd


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


def build_hr_export_df(hr_df: pd.DataFrame) -> pd.DataFrame:
    export_cols: dict[str, str] = {
        "subject_id": "subject_id",
        "value": "heart_rate_bpm",
        "unit": "unit",
        "ts_utc": "startDate_UTC",
        "ts_local": "startDate_local",
    }

    available = {k: v for k, v in export_cols.items() if k in hr_df.columns}
    df = hr_df[list(available.keys())].rename(columns=available).copy()

    if "startDate_UTC" in df.columns:
        df = df.sort_values("startDate_UTC")

    return df


def build_sleep_export_df(sleep_df: pd.DataFrame) -> pd.DataFrame:
    sleep_df = sleep_df.copy()

    if "duration_s" in sleep_df.columns:
        sleep_df["duration_minutes"] = (sleep_df["duration_s"] / 60).round(2)

    export_cols: dict[str, str] = {
        "subject_id": "subject_id",
        "stage": "sleep_stage",
        "raw_value": "raw_value_HK",
        "start_utc": "startDate_UTC",
        "end_utc": "endDate_UTC",
        "start_local": "startDate_local",
        "end_local": "endDate_local",
        "duration_minutes": "duration_minutes",
    }

    available = {k: v for k, v in export_cols.items() if k in sleep_df.columns}
    df = sleep_df[list(available.keys())].rename(columns=available).copy()

    if "startDate_UTC" in df.columns:
        df = df.sort_values("startDate_UTC")

    return df


def subject_csv_filename(base: str, subject_ids: list[str]) -> str:
    if len(subject_ids) == 1:
        return f"{base}_{subject_ids[0]}.csv"

    return f"{base}_vsetci_subjekti.csv"