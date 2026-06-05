"""Graf trendu srdcovej frekvencie."""
import streamlit as st
import plotly.express as px
import pandas as pd


def render(filtered_raw_hr: pd.DataFrame) -> None:
    """Renderuje graf trendu HR (FR-013)."""
    if len(filtered_raw_hr) == 0:
        st.warning("Žiadne dáta srdcovej frekvencie na zobrazenie.")
        return

    st.markdown("### Trend srdcovej frekvencie")

    fig = px.scatter(
        filtered_raw_hr,
        x="ts_local",
        y="value",
        title="Srdcová frekvencia v čase",
        labels={"ts_local": "Čas", "value": "HR (bpm)"},
        template="health",
    )

    fig.update_layout(height=400, hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    with st.expander("🔬 Vedecké vysvetlenie grafu", expanded=False):
        st.markdown(
            """
**Čo tento graf zobrazuje?**
Graf znázorňuje každé jednotlivé meranie srdcovej frekvencie (HR) v čase ako body. Os X je čas, os Y je hodnota HR v úderoch za minútu (bpm).

**Ako výsledky interpretovať?**
- Viditeľný **pokles HR v nočných hodinách** je fyziologicky normálny a žiaduci — ide o prejav nočného dippingu, ktorý naznačuje, že parasympatický nervový systém správne spomalil srdce počas odpočinku.
- **Trvalo zvýšené hodnoty** (nad 100 bpm v pokoji) môžu orientačne naznačovať zvýšený stres, dehydratáciu, infekciu alebo pretrénovanosť — nie sú však diagnostickým nástrojom.
- **Jednotlivé špičky** (krátke výrazné zvýšenia) sú často spôsobené pohybom, pohybovými artefaktmi senzora alebo krátkymi záťažovými momentmi.

**Obmedzenia merania:**
Apple Watch meria HR optickou pletyzmografiou (PPG). Presnosť môže byť nižšia pri rýchlom pohybe, chlade alebo nesprávnom nasadení zariadenia. Táto aplikácia slúži ako **podporný vizualizačný nástroj**, nie ako medicínska diagnostika.
"""
        )
