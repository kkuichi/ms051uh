import streamlit as st
import pandas as pd


def render_kpis(
    filtered_nightly_df: pd.DataFrame,
    filtered_raw_hr: pd.DataFrame,
) -> None:
    col1, col2, col3 = st.columns(3)

    if len(filtered_raw_hr) > 0:
        avg_hr = filtered_raw_hr["value"].mean()
        col1.metric("Priemerná HR", f"{avg_hr:.0f} bpm")
    else:
        col1.metric("Priemerná HR", "—")

    if len(filtered_raw_hr) > 0:
        max_hr = filtered_raw_hr["value"].max()
        col2.metric("Maximálna HR", f"{max_hr:.0f} bpm")
    else:
        col2.metric("Maximálna HR", "—")

    if len(filtered_nightly_df) > 0 and "total_sleep_s" in filtered_nightly_df.columns:
        total_sleep_s = filtered_nightly_df["total_sleep_s"].sum()
        total_sleep_h = total_sleep_s / 3600
        col3.metric("Celkový spánok", f"{total_sleep_h:.1f} h")
    else:
        col3.metric("Celkový spánok", "—")