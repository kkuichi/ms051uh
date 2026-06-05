"""Časová os spánkových fáz."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from health_dashboard.ui.theme import STAGE_COLORS


def render(filtered_raw_sleep: pd.DataFrame) -> None:
    """Renderuje časovú os spánkových fáz (FR-014)."""
    if len(filtered_raw_sleep) == 0:
        st.warning("Žiadne dáta spánku na zobrazenie.")
        return

    st.markdown("### Časová os spánkových fáz")

    fig = go.Figure()

    for stage in filtered_raw_sleep["stage"].unique():
        stage_data = filtered_raw_sleep[filtered_raw_sleep["stage"] == stage]
        fig.add_trace(
            go.Bar(
                x=stage_data["start_local"],
                y=stage_data["duration_s"] / 60,
                name=stage,
                marker_color=STAGE_COLORS.get(stage, "#999999"),
                text=[f"{d/60:.0f}m" for d in stage_data["duration_s"]],
                textposition="inside",
            )
        )

    fig.update_layout(
        title="Spánkové fázy – časová os",
        xaxis_title="Čas",
        yaxis_title="Trvanie (minúty)",
        barmode="stack",
        height=400,
        template="health",
        hovermode="x unified",
    )

    st.plotly_chart(fig, width="stretch")

    with st.expander("🔬 Vedecké vysvetlenie grafu", expanded=False):
        st.markdown(
            """
**Čo tento graf zobrazuje?**
Graf zobrazuje štruktúru spánku (tzv. hypnogram) – rozloženie spánkových fáz počas každej noci. Každý farebný blok predstavuje jeden interval jednej spánkovej fázy, jeho výška zodpovedá dĺžke trvania v minútach.

**Vysvetlenie fáz:**
| Fáza | Popis |
|------|-------|
| **Core** | Ľahký spánok (fázy N1 + N2 podľa AASM); tvorí väčšinu spánku |
| **Deep** | Hlboký spánok (fáza N3, pomalé delta vlny); fyzická regenerácia tela |
| **REM** | Fáza rýchlych očných pohybov; konsolidácia pamäti a emocionálne spracovanie |
| **Awake** | Prebudenie počas noci; krátke prebudenia sú fyziologicky normálne |
| **InBed** | Čas strávený v posteli bez zaznamenaného aktívneho spánku |

**Ako výsledky interpretovať?**
- Zdravý spánok obsahuje **pravidelne sa striedajúce cykly** trvajúce 90–120 minút.
- **Dostatok Deep fázy** (odporúčane 15–20 % celkového spánku) naznačuje dobrú fyzickú regeneráciu.
- **Absencia REM alebo Deep fázy** môže orientačne naznačovať nekvalitný spánok, vplyv alkoholu, liekov alebo rušivého prostredia — nie je to však diagnostický záver.

Výsledky sú **orientačné** a klasifikácia fáz pochádza z akcelerometra a HR senzora Apple Watch, nie z klinickej polysomnografie (EEG).
"""
        )
