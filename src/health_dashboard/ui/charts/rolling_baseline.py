"""Vizualizácia kĺzavej základnej línie a stresového indikátora."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(filtered_nightly_df: pd.DataFrame) -> None:
    """Renderuje graf kĺzavej základnej línie a stresového indikátora (FR-030, FR-031)."""
    if len(filtered_nightly_df) == 0:
        st.warning("Žiadne dáta na zobrazenie.")
        return

    if "roll_7d_deep_hr" not in filtered_nightly_df.columns:
        st.warning("Nedostatok dát pre kĺzavý priemer (potrebných ≥ 7 nocí).")
        return

    st.markdown("### Kĺzavá základná línia a stresový indikátor")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_nightly_df.index,
            y=filtered_nightly_df["mean_deep"],
            name="Deep HR (nočná)",
            mode="lines+markers",
            line=dict(color="#1D3557"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_nightly_df.index,
            y=filtered_nightly_df["roll_7d_deep_hr"],
            name="7-dňový kĺzavý priemer",
            mode="lines",
            line=dict(color="#4E79A7", dash="dash"),
        )
    )

    if "stress_flag" in filtered_nightly_df.columns:
        stress_nights = filtered_nightly_df[filtered_nightly_df["stress_flag"]]
        if len(stress_nights) > 0:
            fig.add_trace(
                go.Scatter(
                    x=stress_nights.index,
                    y=stress_nights["mean_deep"],
                    name="Stresový indikátor",
                    mode="markers",
                    marker=dict(size=10, color="red", symbol="star"),
                )
            )

    fig.update_layout(
        title="Deep HR vs 7-dňová základná línia",
        xaxis_title="Noc",
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
Graf porovnáva priemernú HR počas hlbokého spánku (Deep HR) každej noci s jej 7-dňovým kĺzavým priemerom (základnou líniou). Červené hviezdy označujú noci so **stresovým indikátorom**.

**Čo je kĺzavá základná línia?**
Kĺzavý priemer vyhladí krátkodobé výkyvy a odhalí dlhodobý trend. 7-dňová základná línia zodpovedá priemeru posledných 7 nocí — pomáha odhaliť, či sa Deep HR trvalo zvyšuje alebo znižuje.

**Stresový indikátor (červené hviezdy):**
Stresový indikátor sa aktivuje, keď Deep HR **prekročí 7-dňovú základnú líniu o ≥ 3 bpm na 2 alebo viac po sebe nasledujúcich nociach**. Môže orientačne naznačovať:
- Počínajúcu infekciu alebo chorobu
- Pretrénovanie a nedostatočnú regeneráciu
- Chronický stres alebo nedostatok spánku
- Zmenu životosprávy (alkohol, cestovanie, časové pásmo)

**Upozornenie:**
Stresový indikátor je **výlučne orientačný** a automatizovaný — nie je diagnostickým nástrojom. Izolované zvýšenie môže mať bežné fyziologické príčiny. Ak vás výsledky znepokojujú, konzultujte ich s lekárom.
"""
        )
