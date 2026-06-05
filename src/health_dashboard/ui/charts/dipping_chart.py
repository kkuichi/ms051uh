"""Graf nočného HR dippingu."""
import streamlit as st
import plotly.express as px
import pandas as pd


def render(filtered_nightly_df: pd.DataFrame) -> None:
    """Renderuje graf nočného HR dippingu (FR-029)."""
    if len(filtered_nightly_df) == 0:
        st.warning("Žiadne dáta na zobrazenie.")
        return

    if "dip_pct" not in filtered_nightly_df.columns:
        st.warning("Dáta pre nočný dipping nie sú dostupné.")
        return

    st.markdown("### Nočný HR dipping")

    display_df = filtered_nightly_df[["dip_pct", "dip_classification"]].copy().reset_index()

    color_map = {
        "healthy": "#2ecc71",
        "reduced": "#f39c12",
        "non-dipper": "#e74c3c",
        "N/A": "#95a5a6",
    }

    fig = px.bar(
        display_df,
        x="night_date",
        y="dip_pct",
        color="dip_classification",
        color_discrete_map=color_map,
        title="Nočný HR dipping podľa noci",
        labels={"night_date": "Noc", "dip_pct": "Dipping (%)"},
        template="health",
    )

    fig.add_hline(
        y=10, line_dash="dash", line_color="green",
        annotation_text="Zdravý prah (10 %)"
    )
    fig.add_hline(
        y=0, line_dash="dash", line_color="red",
        annotation_text="Nulový prah"
    )

    fig.update_layout(height=400, hovermode="x unified")

    st.plotly_chart(fig, width="stretch")

    with st.expander("🔬 Vedecké vysvetlenie grafu", expanded=False):
        st.markdown(
            """
**Čo tento graf zobrazuje?**
Graf zobrazuje percentuálny pokles srdcovej frekvencie (HR) počas hlbokého spánku (Deep) v porovnaní s predspanou základnou hodnotou (baseline). Táto hodnota sa nazýva **nočný HR dipping**.

**Výpočet:** `dipping (%) = ((baseline HR − Deep HR) / baseline HR) × 100`

Kde *baseline HR* je priemerná HR 30 minút pred zaspaním a *Deep HR* je priemerná HR počas Deep fázy danej noci.

**Klasifikácia výsledkov:**
| Farba | Hodnota | Interpretácia |
|-------|---------|---------------|
| 🟢 Zelená | ≥ 10 % | Fyziologický (zdravý) dipping — autonómny nervový systém správne funguje |
| 🟠 Oranžová | 0 – 10 % | Znížený dipping — môže orientačne naznačovať zvýšenú záťaž organizmu |
| 🔴 Červená | < 0 % | Non-dipper — HR počas Deep spánku neklesla; môže ísť o artefakt merania alebo skrátenie Deep fázy |

**Dôležité upozornenie:**
Nočný dipping je **orientačný ukazovateľ** fyziologickej regulácie srdca. Nízke alebo záporné hodnoty môžu mať mnoho príčin vrátane krátkej Deep fázy, pohybových artefaktov, zlej polohy zariadenia, ale aj reálnych fyziologických faktorov. Táto aplikácia **nediagnostikuje ochorenia** — výsledky interpretujte v kontexte a v prípade pochybností sa poraďte s lekárom.
"""
        )
