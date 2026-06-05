"""Kombinovaný pohľad HR + spánkové fázy."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from health_dashboard.ui.theme import STAGE_COLORS


def render(
    filtered_aligned_hr: pd.DataFrame,
    filtered_raw_sleep: pd.DataFrame,
) -> None:
    """Renderuje kombinovaný pohľad HR a spánku (FR-015)."""
    if len(filtered_aligned_hr) == 0:
        st.warning("Žiadne dáta na zobrazenie.")
        return

    st.markdown("### Srdcová frekvencia počas spánku podľa fáz")

    fig = go.Figure()

    for stage in filtered_aligned_hr["stage"].unique():
        stage_data = filtered_aligned_hr[filtered_aligned_hr["stage"] == stage]
        fig.add_trace(
            go.Scatter(
                x=stage_data["ts_local"],
                y=stage_data["value"],
                name=stage,
                mode="markers",
                marker=dict(size=4, color=STAGE_COLORS.get(stage, "#999999")),
            )
        )

    fig.update_layout(
        title="HR podľa spánkovej fázy",
        xaxis_title="Čas",
        yaxis_title="HR (bpm)",
        height=400,
        template="health",
        hovermode="x unified",
    )

    st.plotly_chart(fig, width="stretch")

    with st.expander("🔬 Vedecké vysvetlenie grafu", expanded=False):
        st.markdown(
            """
**Čo tento graf zobrazuje?**
Graf kombinuje merania srdcovej frekvencie s informáciou o spánkovej fáze, v ktorej bolo každé meranie zaznamenané. Každý bod je jedno meranie HR; farba bodu určuje spánkovú fázu.

**Ako výsledky interpretovať?**
- **Deep (hlboký spánok):** Očakávajte najnižšie hodnoty HR — dominuje parasympatický nervový systém, srdce spomaľuje, telo sa fyzicky regeneruje.
- **Core (ľahký spánok):** HR je o niečo vyššia ako v Deep fáze, ale výrazne nižšia ako v bdelosti.
- **REM:** HR môže kolísať a priblížiť sa hodnotám z bdelosti — zvýšená mozgová aktivita počas snívania je fyziologicky normálna.
- **Wake/Out-of-sleep:** Merania mimo spánkových intervalov — denné hodnoty alebo prebudenia.

**Na čo si dať pozor?**
Ak sú hodnoty HR v Deep fáze trvalo rovnako vysoké ako cez deň, môže to orientačne naznačovať vonkajší stresor, dehydratáciu alebo počínajúce ochorenie. Tieto pozorovania sú však len **podporným vizualizačným nástrojom** a nevypovedajú jednoznačne o zdravotnom stave.
"""
        )
