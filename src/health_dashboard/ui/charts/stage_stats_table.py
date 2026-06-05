"""Tabuľka štatistík spánkových fáz."""
import streamlit as st
import pandas as pd


def render(filtered_nightly_df: pd.DataFrame) -> None:
    """Renderuje tabuľku štatistík spánkových fáz (FR-027)."""
    if len(filtered_nightly_df) == 0:
        st.warning("Žiadne dáta na zobrazenie.")
        return

    st.markdown("### Štatistiky srdcovej frekvencie podľa spánkových fáz")

    stage_cols = [
        col for col in filtered_nightly_df.columns if "mean_" in col or "std_" in col
    ]

    if not stage_cols:
        st.warning("Žiadne štatistiky fáz nie sú dostupné.")
        return

    display_df = filtered_nightly_df[stage_cols].copy()
    display_df = display_df.round(1)

    # Slovenské názvy stĺpcov
    rename_map = {
        "mean_core": "Priemer Core (bpm)",
        "mean_deep": "Priemer Deep (bpm)",
        "mean_rem": "Priemer REM (bpm)",
        "mean_awake": "Priemer Awake (bpm)",
        "std_core": "Std Core",
        "std_deep": "Std Deep",
        "std_rem": "Std REM",
    }
    display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})

    st.dataframe(display_df, width="stretch")

    with st.expander("📘 Vysvetlenie pojmov v tabuľke", expanded=False):
        st.markdown(
            """
**Vysvetlenie stĺpcov a pojmov:**

| Pojem | Vysvetlenie |
|-------|-------------|
| **Priemer** (mean) | Priemerná hodnota srdcovej frekvencie (HR) nameraná počas danej spánkovej fázy v príslušnú noc. Udáva sa v bpm (údery za minútu). |
| **Std** (smerodajná odchýlka) | Miera variability HR počas danej fázy. Nízka hodnota = HR bola stabilná; vysoká hodnota = HR počas noci výrazne kolísala. |
| **Core** | Ľahký spánok (zodpovedá fázam N1 + N2 podľa klinickej klasifikácie AASM). Tvorí najväčšiu časť spánku. |
| **Deep** | Hlboký spánok (fáza N3, pomalé delta vlny). Kľúčový pre fyzickú regeneráciu. HR je tu zvyčajne najnižšia. |
| **REM** | Fáza rýchlych očných pohybov (sny). Dôležitá pre pamäť a emocionálne spracovanie. HR môže kolísať a byť vyššia ako v Deep. |
| **Awake** | Prebudenie zaznamenané počas noci. Krátke prebudenia sú fyziologicky normálne. |
| **bpm** | Beats per minute — počet úderov srdca za minútu. Referenčné hodnoty pre dospelých v pokoji: 60–100 bpm. |
| **NaN** | Not a Number — chýbajúca hodnota. Znamená, že daná noc nemala dostatok HR meraní v tejto fáze na výpočet štatistiky (napr. Deep fáza trvala príliš krátko alebo nebola zaznamenaná). |
| **mean_deep** | Priemerná HR počas Deep (hlbokého) spánku. Táto hodnota je kľúčovým vstupom pre výpočet nočného dippingu a stresového indikátora. |
"""
        )

    with st.expander("🔬 Vedecké vysvetlenie tabuľky", expanded=False):
        st.markdown(
            """
**Prečo sledovať HR podľa spánkových fáz?**

Hodnota srdcovej frekvencie nie je počas spánku konštantná — mení sa v závislosti od spánkovej fázy a odráža stav autonómneho nervového systému:

- Počas **Deep (hlbokého) spánku** dominuje parasympatický nervový systém, ktorý spomaľuje srdce. Nízka a stabilná HR v tejto fáze naznačuje kvalitnú fyzickú regeneráciu.
- Počas **REM** mozgová aktivita stúpa, HR môže kolísať a dosahovať hodnoty blízke bdelosti — to je fyziologicky normálne.
- Počas **Core** fázy je HR mierne nižšia ako v bdelosti, no vyššia ako v Deep.

**Ako výsledky interpretovať?**
Tabuľka slúži ako **podporný vizualizačný nástroj** na orientačné porovnanie nočných HR hodnôt. Výrazné odchýlky medzi nocami (napr. trvalo vyšší `mean_deep`) môžu orientačne naznačovať zmeny v regenerácii organizmu, nie sú však diagnostickým záverom. Výsledky sú závislé od presnosti klasifikácie fáz algoritmom Apple Watch.
"""
        )
