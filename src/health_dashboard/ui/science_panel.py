import streamlit as st


def render_science_panel() -> None:

    st.markdown("## 🔬 Vedecké okienko")
    st.caption(
        "Táto sekcia poskytuje prehľad fyziologických základov "
        "monitorovaných ukazovateľov. Slúži ako **podporný vzdelávací doplnok** k orientačnej "
        "analýze dát a zároveň ako podklad pre interpretáciu výsledkov. "
        "Aplikácia **nediagnostikuje ochorenia** — výsledky sú orientačné."
    )


    with st.expander("❤️ 1. Srdcová frekvencia (HR – Heart Rate)", expanded=False):
        st.markdown(
            """
**Srdcová frekvencia** označuje počet kontrakcií (úderov) srdca za minútu
(bpm – beats per minute). Je jedným zo základných vitálnych znakov a
citlivým indikátorom fyziologického stavu organizmu.

#### Pokojová srdcová frekvencia (RHR – Resting Heart Rate)

Pokojová srdcová frekvencia sa meria v stave fyzického a psychického kľudu,
zvyčajne ráno po prebudení pred vstávaním z postele. Odráža efektivitu
srdcovo-cievneho systému a celkovú úroveň aeróbnej zdatnosti.

**Referenčné hodnoty pre dospelých (podľa AHA):**

| Kategória | RHR (bpm) |
|-----------|-----------|
| Výborná kondícia (napr. vytrvalostní športovci) | 40 – 60 |
| Normálna hodnota | 60 – 100 |
| Zvýšená hodnota (tachykardia v pokoji) | > 100 |
| Bradykardia | < 60 |

> *Hodnoty pod 60 bpm u trénovaných jedincov zvyčajne nepredstavujú
> patológiu, ale fyziologickú adaptáciu na pravidelný aeróbny tréning.*

**Klinický význam:**
Dlhodobé sledovanie RHR umožňuje orientačne identifikovať trendy spojené
s pretrénovaním, infekciou, stresom alebo kardiovaskulárnymi rizikami.
Štúdia Larsson et al. (2021) preukázala, že každé zvýšenie RHR o 10 bpm
je spojené s 16 % nárastom rizika kardiovaskulárnych príhod.

> ⚠️ Tieto informácie slúžia len na vzdelávacie účely. Táto aplikácia
> **nediagnostikuje** žiadne ochorenia — výsledky sú orientačné.
"""
        )

   
    with st.expander("😴 2. Spánok a jeho fyziológia", expanded=False):
        st.markdown(
            """
**Spánok** je dynamický fyziologický proces nevyhnutný pre regeneráciu
centrálneho nervového systému, konsolidáciu pamäti, imunitnú funkciu
a hormonálnu reguláciu. Podľa odporúčaní National Sleep Foundation by
dospelí mali spať 7–9 hodín denne.

#### Spánkové fázy – štruktúra spánkového cyklu

Spánok sa člení na opakujúce sa 90–120 minútové cykly, pričom každý
cyklus zahŕňa fázy NREM a REM:

```
N1 → N2 → N3 → N2 → REM → (nový cyklus)
```

| Fáza | Označenie | Popis |
|------|-----------|-------|
| N1 | Ľahký spánok | Prechod bdelosť → spánok; ľahko prebuditeľný |
| N2 | Ľahký spánok | Spánkové vretienka, K-komplexy; pokles teploty a HR |
| N3 | Hlboký spánok (SWS) | Pomalé delta vlny; fyzická regenerácia; ťažko prebuditeľný |
| REM | Rapid Eye Movement | Sny; konsolidácia pamäti; vysoká mozgová aktivita |

**Apple Watch terminológia:**

| Apple HealthKit identifikátor | Zobrazenie v aplikácii |
|-------------------------------|------------------------|
| `AsleepCore` | Core (fázy N1 + N2) |
| `AsleepDeep` | Deep (fáza N3 – hlboký spánok) |
| `AsleepREM` | REM |
| `Awake` | Awake (prebudenie počas noci) |
| `InBed` | InBed (čas v posteli bez aktívneho spánku) |
"""
        )

    
    with st.expander("📉 3. Srdcová frekvencia počas spánku a nočný dipping", expanded=False):
        st.markdown(
            """
Počas spánku dochádza k charakteristickým zmenám HR riadených autonómnym
nervovým systémom:

- **NREM (N2, N3):** Dominancia parasympatiku → výrazný pokles HR
  (typicky 10–30 % pod dennú pokojovú hodnotu)
- **REM:** Parasympatická aktivita klesá, HR sa kolíše a môže dosiahnuť
  hodnoty blízke bdeniu alebo ich aj prekročiť

#### Nočný HR dipping

**Nočný dipping** označuje percentuálny pokles priemernej nočnej HR
voči predspanej základnej hodnote. Výpočet:

`dipping (%) = ((baseline HR − Deep HR) / baseline HR) × 100`

| Klasifikácia | Hodnota | Orientačný význam |
|-------------|---------|-------------------|
| Fyziologický (healthy) | ≥ 10 % | Zdravá kardiovaskulárna regulácia |
| Znížený (reduced) | 0 – 10 % | Môže orientačne naznačovať zvýšenú záťaž |
| Non-dipper | < 0 % | HR neklesla; môže ísť o artefakt alebo fyziologický faktor |

> Tieto klasifikácie sú **orientačné** a nevypovedajú jednoznačne
> o zdravotnom stave. Aplikácia nie je medicínska diagnostika.
"""
        )

    
    with st.expander("🔗 4. Prečo sledovať HR a spánok spoločne?", expanded=False):
        st.markdown(
            """
Integrácia dát o srdcovej frekvencii a spánkovej architektúre poskytuje
komplexnejší pohľad na regeneráciu a zdravotný stav ako každý z ukazovateľov
samostatne:

1. **Hodnotenie kvality spánku** – Fyziologický pokles HR v hlbokom spánku
   môže orientačne potvrdzovať kvalitný odpočinok
2. **Detekcia pretrénovania** – Trvalo zvýšená nočná HR môže naznačovať
   nedostatočnú regeneráciu
3. **Sledovanie trendov** – Dlhodobé zmeny RHR a nočného dippingu sú
   klinicky sledovanými ukazovateľmi (nejde o diagnostiku v tejto aplikácii)
4. **Personalizovaná spätná väzba** – Kombinácia metrík umožňuje
   orientačne identifikovať konkrétne noci s potenciálne narušenou regeneráciou

> Všetky závery tejto aplikácie sú **orientačné** a slúžia ako
> **podporný vizualizačný nástroj**, nie ako medicínske odporúčanie.
"""
        )

    
    with st.expander("⚠️ 5. Obmedzenia dát z wearables – metodologické poznámky", expanded=False):
        st.markdown(
            """
Pri interpretácii dát z nositeľných zariadení (wearables) je nevyhnutné
zohľadniť nasledujúce metodologické obmedzenia:

- **Presnosť optickej pletyzmografie (PPG):** Apple Watch meria HR pomocou
  zeleného LED svetla a fotodiódy. Presnosť môže byť znížená pri
  pohybových artefaktoch, nízkej perfúzii (chlad), tmavšom odtieni pokožky
  alebo nesprávnom nasadení zariadenia.
- **Klasifikácia spánkových fáz:** Apple Watch určuje spánkové fázy
  z kombinácie akcelerometrických dát, HR a vzorcov dýchania – nie
  z polysomnografie (EEG/EOG/EMG). Presnosť klasifikácie je nižšia
  ako pri klinickom vyšetrení.
- **Výber subjektu:** Údaje pochádzajú od jedného subjektu; výsledky
  nie sú generalizovateľné na populáciu.
- **Denná variabilita:** Srdcová frekvencia je ovplyvnená hydratáciou,
  kofeínom, alkoholom, stresom, cestovaním a ďalšími faktormi,
  ktoré dataset neobsahuje.

> Táto aplikácia je **akademický podporný vizualizačný nástroj**.
> Výsledky **nenahrádzajú lekárske vyšetrenie ani diagnostiku**.
"""
        )

    
    with st.expander("📚 6. Odporúčané zdroje a literatúra", expanded=False):
        st.markdown(
            """
| # | Zdroj | Relevancia |
|---|-------|------------|
| 1 | American Heart Association. (2023). *Heart Rate* | Referenčné hodnoty HR |
| 2 | Hirshkowitz, M. et al. (2015). NSF sleep duration recommendations. *Sleep Health, 1*(1), 40–43. | Odporúčaná dĺžka spánku |
| 3 | Berry, R. B. et al. (2017). *AASM Manual for Scoring of Sleep and Associated Events* (v2.4). | Klasifikácia spánkových fáz |
| 4 | Larsson, S. C. et al. (2021). Resting heart rate and CV risk. *BMC Medicine, 19*, 15. | Klinický význam RHR |
| 5 | Perez, M. V. et al. (2019). Large-scale assessment of a smartwatch. *NEJM, 381*, 1909–1917. | Validita wearable HR meraní |
| 6 | Apple Inc. (2023). *HealthKit Framework Reference* | Formát dát Apple Health |

---
*Táto sekcia slúži ako metodologický komentár a základ pre diskusiu
výsledkov. Konkrétne hodnoty z vašich dát sú zobrazené v analytických
sekciách aplikácie. Výsledky sú **orientačné** a aplikácia slúži ako
**podporný vizualizačný nástroj**.*
"""
        )
