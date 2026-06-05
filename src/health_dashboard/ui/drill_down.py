import streamlit as st
import pandas as pd


def render(filtered_nightly_df: pd.DataFrame) -> None:
    if len(filtered_nightly_df) == 0:
        st.warning("Žiadne dáta na zobrazenie.")
        return

    st.markdown("### Detailný prehľad podľa nocí")
    st.caption(
        "Tabuľka zobrazuje vypočítané metriky pre každú noc v zvolenom rozsahu. "
        "Každý riadok predstavuje jednu noc. "
        "Stĺpce zobrazujú počet HR meraní, priemernú HR v jednotlivých fázach, "
        "klasifikáciu dippingu a stresový indikátor."
    )

    display_cols = [
        "n_hr_samples",
        "mean_deep",
        "mean_core",
        "mean_rem",
        "dip_pct",
        "dip_classification",
        "stress_flag",
    ]

    available_cols = [
        col for col in display_cols if col in filtered_nightly_df.columns
    ]

    if not available_cols:
        st.warning("Žiadne metriky nie sú dostupné.")
        return

    display_df = filtered_nightly_df[available_cols].copy()

    num_cols = display_df.select_dtypes(include="number").columns
    display_df[num_cols] = display_df[num_cols].round(1)

    rename_map = {
        "n_hr_samples": "Počet HR meraní",
        "mean_deep": "Deep HR (bpm)",
        "mean_core": "Core HR (bpm)",
        "mean_rem": "REM HR (bpm)",
        "dip_pct": "Dipping (%)",
        "dip_classification": "Klasifikácia",
        "stress_flag": "Stresový indikátor",
    }

    display_df = display_df.rename(
        columns={k: v for k, v in rename_map.items() if k in display_df.columns}
    )

    st.dataframe(display_df, width="stretch", height=400)