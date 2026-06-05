from __future__ import annotations

import re

import pandas as pd


def _extract_person_key(source: str) -> str:
    match = re.match(r"^(.+?)'s?\s", source.strip(), re.IGNORECASE)

    if match:
        return match.group(1).strip().lower()

    return f"__app__{source}"


def build_subject_mapping(
    *source_series: pd.Series,
) -> dict[str, str]:
    unique_sources: set[str] = set()

    for s in source_series:
        unique_sources.update(s.dropna().astype(str).unique())

    person_key_to_sources: dict[str, list[str]] = {}

    for src in unique_sources:
        key = _extract_person_key(src)
        person_key_to_sources.setdefault(key, []).append(src)

    person_keys = sorted(
        k for k in person_key_to_sources
        if not k.startswith("__app__")
    )

    app_keys = [
        k for k in person_key_to_sources
        if k.startswith("__app__")
    ]

    mapping: dict[str, str] = {}

    for i, key in enumerate(person_keys, start=1):
        code = f"subjekt_{i:02d}"

        for src in person_key_to_sources[key]:
            mapping[src] = code

    for key in app_keys:
        for src in person_key_to_sources[key]:
            mapping[src] = "subjekt_app"

    return mapping


def anonymize_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, str],
    source_col: str = "source_raw",
    output_col: str = "subject_id",
) -> pd.DataFrame:
    df = df.copy()

    if source_col in df.columns:
        df[output_col] = (
            df[source_col]
            .map(mapping)
            .fillna("subjekt_01")
        )

        df = df.drop(columns=[source_col])

    else:
        df[output_col] = "subjekt_01"

    drop_if_present = {
        "device",
        "sourceName",
        "source",
        "sourceVersion",
    }

    df = df.drop(
        columns=[c for c in drop_if_present if c in df.columns]
    )

    return df


def inject_placeholder_source(
    df: pd.DataFrame,
    col: str = "source_raw",
) -> pd.DataFrame:
    df = df.copy()

    if col not in df.columns:
        df[col] = "csv_upload"

    return df