from datetime import date, timedelta
import streamlit as st
import pandas as pd


def _to_date(value, fallback: date) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, (list, tuple)) and len(value) > 0:
        first = value[0]
        if isinstance(first, date):
            return first
        if isinstance(first, pd.Timestamp):
            return first.date()
    return fallback


def _normalize_range_value(value, fallback: date, which: str = "start") -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return fallback
        candidate = value[1] if (which == "end" and len(value) > 1) else value[0]
        if isinstance(candidate, date):
            return candidate
        if isinstance(candidate, pd.Timestamp):
            return candidate.date()
    return fallback


def week_label(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso[0]}-T{iso[1]:02d}"


def week_bounds(label: str) -> tuple[date, date]:
    year = int(label[:4])
    week = int(label[6:])
    monday = date.fromisocalendar(year, week, 1)
    return monday, monday + timedelta(days=6)


def _month_label(d: date) -> str:
    return d.strftime("%Y-%m")


def _month_bounds(label: str) -> tuple[date, date]:
    year, month = int(label[:4]), int(label[5:7])
    first = date(year, month, 1)
    last = date(year + 1, 1, 1) - timedelta(days=1) if month == 12 else date(year, month + 1, 1) - timedelta(days=1)
    return first, last


def render_sidebar(nightly_df: pd.DataFrame) -> tuple[date, date]:
    """Renderuje sidebar s výberom dátového rozsahu; vracia (start_date, end_date)."""
    if len(nightly_df) == 0:
        today = date.today()
        return today - timedelta(days=7), today

    index_dates = []
    for x in nightly_df.index.tolist():
        if isinstance(x, pd.Timestamp):
            index_dates.append(x.date())
        elif isinstance(x, date):
            index_dates.append(x)
        else:
            index_dates.append(pd.to_datetime(x).date())

    all_dates = sorted(index_dates)
    min_date = min(all_dates)
    max_date = max(all_dates)

    st.sidebar.markdown("## 📅 Dátumový rozsah")

    mode_options = ["Týždeň", "Mesiac", "Vlastný"]
    saved_mode_index = st.session_state.get("date_mode_index", 2)
    if saved_mode_index not in [0, 1, 2]:
        saved_mode_index = 2

    mode = st.sidebar.radio(
        "Zobraziť podľa",
        options=mode_options,
        index=saved_mode_index,
        key="date_mode",
    )
    st.session_state.date_mode_index = mode_options.index(mode)

    if mode == "Týždeň":
        week_labels = sorted(set(week_label(d) for d in all_dates))
        default_week = st.session_state.get("selected_week", week_labels[-1])
        if default_week not in week_labels:
            default_week = week_labels[-1]

        selected_week = st.sidebar.selectbox(
            "Kalendárny týždeň",
            options=week_labels,
            index=week_labels.index(default_week),
            key="selected_week",
        )

        start_date, end_date = week_bounds(selected_week)
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)
        st.sidebar.caption(f"📅 {start_date} → {end_date}")

    elif mode == "Mesiac":
        month_labels = sorted(set(_month_label(d) for d in all_dates))
        default_month = st.session_state.get("selected_month", month_labels[-1])
        if default_month not in month_labels:
            default_month = month_labels[-1]

        selected_month = st.sidebar.selectbox(
            "Kalendárny mesiac",
            options=month_labels,
            index=month_labels.index(default_month),
            key="selected_month",
        )

        start_date, end_date = _month_bounds(selected_month)
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)
        st.sidebar.caption(f"📅 {start_date} → {end_date}")

    else:
        raw_default_start = st.session_state.get("custom_start", min_date)
        raw_default_end = st.session_state.get("custom_end", max_date)

        default_start = _normalize_range_value(raw_default_start, min_date, which="start")
        default_end = _normalize_range_value(raw_default_end, max_date, which="end")
        default_start = max(min(default_start, max_date), min_date)
        default_end = max(min(default_end, max_date), min_date)
        if default_start > default_end:
            default_start, default_end = default_end, default_start

        date_range = st.sidebar.date_input(
            "Dátumový rozsah (od → do)",
            value=(default_start, default_end),
            min_value=min_date,
            max_value=max_date,
            key="custom_date_input",
        )

        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date = _to_date(date_range[0], min_date)
            end_date = _to_date(date_range[1], max_date)
        else:
            single_date = _to_date(date_range, min_date)
            start_date = end_date = single_date

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        st.session_state.custom_start = start_date
        st.session_state.custom_end = end_date
        st.sidebar.caption(f"📅 {start_date} → {end_date}")

    normalized_index = pd.Index(all_dates)
    nights_in_range = ((normalized_index >= start_date) & (normalized_index <= end_date)).sum()
    st.sidebar.info(f"**{nights_in_range}** nocí v zvolenom rozsahu")

    return start_date, end_date
