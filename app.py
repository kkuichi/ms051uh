"""Health Data Dashboard

Podporovane vstupy:
- Apple Health export.xml
- CSV pary z priecinka tests/data/

Funkcie:
- Vstup dat: CSV pary alebo Apple Health export.xml
- Automaticka anonymizacia osobnych identifikatorov
- CSV export po XML parsovani
- Vedecke okienko s odbornym pozadim metrik
"""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

st.set_page_config(
    page_title="Health Dashboard",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)

from health_dashboard.ui.info_cards import render_info_cards
from health_dashboard.ui.file_upload_v2 import render_upload_panel
from health_dashboard.ui.sidebar import render_sidebar
from health_dashboard.ui.kpi_cards import render_kpis
from health_dashboard.ui.messages import (
    render_empty_state,
    render_ingestion_report,
    render_oom_warning,
    render_insufficient_data,
)
from health_dashboard.ui.theme import register_plotly_template
from health_dashboard.ui import charts
from health_dashboard.ui.drill_down import render as render_drill_down
from health_dashboard.ui.science_panel import render_science_panel
from health_dashboard.analytics.nightly_metrics import compute_nightly_metrics
from health_dashboard.config import (
    LOCAL_TZ,
    MIN_NIGHTS_BASIC_KPIS,
    MIN_NIGHTS_STAGE_STATS,
    MIN_NIGHTS_7D_ROLLING,
)

register_plotly_template()


st.title("💗 Health Data Dashboard")
st.markdown("Analýza dát srdcovej frekvencie a spánku z Apple Watch")


render_info_cards()

st.divider()

# nahranie suborov
raw_hr, raw_sleep = render_upload_panel(local_tz=LOCAL_TZ)

if raw_hr is None or raw_sleep is None:
    render_empty_state(
        "Nahrajte dáta srdcovej frekvencie aj spánku, aby ste spustili analýzu. "
        "Testovacie súbory nájdete v priečinku `tests/data/` "
        "(demo_heartrate.csv a demo_sleep.csv)."
    )
    st.stop()

# metriky
@st.cache_data(max_entries=4, ttl=3600)
def compute_metrics(
    hr_parquet: bytes,
    sleep_parquet: bytes,
    local_tz: str,
):
    """Cachovanie výpočtu nočných metrík a zarovnaného HR."""
    from health_dashboard.alignment.hr_sleep_join import align_hr_to_stages
    import io

    hr_df = pd.read_parquet(io.BytesIO(hr_parquet))
    sleep_df = pd.read_parquet(io.BytesIO(sleep_parquet))

    nightly_df = compute_nightly_metrics(hr_df, sleep_df, local_tz)
    aligned_hr = align_hr_to_stages(hr_df, sleep_df)

    return nightly_df, hr_df, sleep_df, aligned_hr


def _to_parquet_bytes(df: pd.DataFrame) -> bytes:
    """Serializuje DataFrame do parquet bajtov pre cachovanie."""
    import io
    buf = io.BytesIO()
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=["category"]).columns:
        df_copy[col] = df_copy[col].astype(str)
    df_copy.to_parquet(buf, index=False)
    return buf.getvalue()


try:
    nightly_df, raw_hr, raw_sleep, aligned_hr = compute_metrics(
        _to_parquet_bytes(raw_hr),
        _to_parquet_bytes(raw_sleep),
        LOCAL_TZ,
    )
except Exception as e:
    st.error(f"Chyba pri spracovaní dát: {str(e)}")
    st.stop()

# datumovy rozsah
if len(nightly_df) > 0:
    if "sidebar_state_reset" not in st.session_state:
        for key in ["custom_start", "custom_end", "custom_date_input"]:
            st.session_state.pop(key, None)
        st.session_state.sidebar_state_reset = True

    start_date, end_date = render_sidebar(nightly_df)

    filtered_nightly_df = nightly_df.loc[start_date:end_date]

    if "ts_local" in raw_hr.columns:
        try:
            ts_local = pd.to_datetime(raw_hr["ts_local"])
            filtered_raw_hr = raw_hr[
                (ts_local.dt.date >= start_date) & (ts_local.dt.date <= end_date)
            ].copy()
        except Exception:
            filtered_raw_hr = raw_hr.copy()
    else:
        filtered_raw_hr = raw_hr.copy()

    if "start_local" in raw_sleep.columns:
        try:
            start_local = pd.to_datetime(raw_sleep["start_local"])
            end_local = pd.to_datetime(raw_sleep["end_local"])
            filtered_raw_sleep = raw_sleep[
                (start_local.dt.date >= start_date) & (end_local.dt.date <= end_date)
            ].copy()
        except Exception:
            filtered_raw_sleep = raw_sleep.copy()
    else:
        filtered_raw_sleep = raw_sleep.copy()

    if "night_date" in aligned_hr.columns:
        filtered_aligned_hr = aligned_hr[
            (aligned_hr["night_date"] >= start_date)
            & (aligned_hr["night_date"] <= end_date)
        ].copy()
    else:
        filtered_aligned_hr = aligned_hr.copy()

else:
    render_empty_state("Po spracovaní dát neboli nájdené žiadne platné záznamy.")
    st.stop()


st.markdown("## Kľúčové metriky")
render_kpis(filtered_nightly_df, filtered_raw_hr)
st.divider()


st.markdown("## Podrobná analýza")

if len(filtered_nightly_df) >= MIN_NIGHTS_BASIC_KPIS:
    col1, col2 = st.columns(2)
    with col1:
        charts.hr_trend.render(filtered_raw_hr)
    with col2:
        charts.sleep_timeline.render(filtered_raw_sleep)
else:
    render_insufficient_data(len(filtered_nightly_df), MIN_NIGHTS_BASIC_KPIS, "základné grafy")

st.markdown("---")
try:
    charts.combined_view.render(filtered_aligned_hr, filtered_raw_sleep)
except Exception as e:
    st.warning(f"Kombinovaný pohľad nie je dostupný: {e}")

st.markdown("---")
if len(filtered_nightly_df) >= MIN_NIGHTS_STAGE_STATS:
    charts.stage_stats_table.render(filtered_nightly_df)
else:
    render_insufficient_data(len(filtered_nightly_df), MIN_NIGHTS_STAGE_STATS, "štatistiky fáz")

st.markdown("---")
if len(filtered_nightly_df) >= MIN_NIGHTS_7D_ROLLING:
    charts.rolling_baseline.render(filtered_nightly_df)
else:
    render_insufficient_data(len(filtered_nightly_df), MIN_NIGHTS_7D_ROLLING, "kĺzavý priemer")

st.markdown("---")
charts.dipping_chart.render(filtered_nightly_df)

st.markdown("---")
render_drill_down(filtered_nightly_df)

# vedecke okienko
st.markdown("---")
render_science_panel()


st.divider()

col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown(
        "**O dashboarde:** Analyzuje exporty Apple HealthKit pre sledovanie srdcovej "
        "frekvencie, spánkovej architektúry a regeneračných metrík. Všetky dáta sú "
        "spracovávané lokálne – žiadne údaje nie sú zdieľané ani ukladané externe. "
        "Osobné identifikátory sú automaticky anonymizované."
    )

with col_right:
    st.markdown("**Navigácia**")
    if st.button("🔬 Vedecké okienko", help="Prejsť na vedecké pozadie metrík"):
        st.markdown(
            "<a href='#vedecké-okienko' style='display:none'></a>",
            unsafe_allow_html=True,
        )
        
        js = """
<script>
    const el = document.querySelector('[data-testid="stExpander"]');
    if (el) { el.scrollIntoView({behavior: 'smooth'}); }
    // Fallback: scroll to bottom where science panel is rendered
    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
</script>
"""
        st.components.v1.html(js, height=0)
        st.info("📖 Vedecké okienko nájdete na konci stránky (nad touto pätičkou).")

st.caption(
    "Health Data Dashboard"
)
