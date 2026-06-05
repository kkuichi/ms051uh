# Health Data Dashboard

Interaktívna webová aplikácia na analýzu zdravotných dát z Apple Watch (srdcová frekvencia a spánok), vytvorená ako praktický výstup bakalárskej práce.

> ⚕️ **Upozornenie:** Táto aplikácia slúži výhradne na informatívne a akademické účely.

---

## Účel aplikácie

Aplikácia umožňuje analyzovať exportované dáta z Apple HealthKit:

- trendy srdcovej frekvencie (HR) počas dňa a noci
- spánkovú architektúru (fázy Core, Deep, REM, Awake)
- nočný HR dipping (percentuálny pokles HR počas hlbokého spánku)
- 7-dňové a 30-dňové kĺzavé základné línie
- indikátor zvýšenej záťaže (stresový flag)

---

## Podporované vstupy

| Formát | Popis |
|--------|-------|
| `export.xml` | Priamy Apple Health XML export (Zdravie → Profil → Exportovať zdravotné dáta) |
| `heartrate.csv` + `sleep.csv` | CSV páry oddelené bodkočiarkou, UTF-8 s BOM |

### Formát CSV súborov

**heartrate.csv:**
```
id;value;unit;startDate
1;72.0;count/min;2025-07-23 14:39:29 +0100
```

**sleep.csv:**
```
id;value;startDate;endDate
1;HKCategoryValueSleepAnalysisAsleepCore;2025-07-23 22:00:00 +0100;2025-07-24 06:30:00 +0100
```

---

## Lokálne spustenie

### Požiadavky

- Python 3.11+

### Inštalácia

```bash
pip install -r requirements.txt
```

Pre vývojové nástroje :

```bash
pip install -e ".[dev]"
```

### Spustenie

```bash
streamlit run app.py
```

Dashboard bude dostupný na `http://localhost:8501`.

---

### Upload limit – vysvetlenie

Súbor `.streamlit/config.toml` nastavuje `maxUploadSize = 2048` (2 GB).

**Dôvod:** Apple Health XML export rastie s dĺžkou používania zariadenia. Viacročné exporty môžu dosahovať 500 MB až 2 GB. Limit 2 GB pokrýva aj tieto prípady.

**Dôležité obmedzenia Streamlit Community Cloud:**

- Pamäť servera je obmedzená (~1 GB RAM pre bezplatný tier).
- Timeout pri spracovaní je ~15–30 minút.
- Pri exportoch väčších ako ~500 MB môže nastať timeout alebo zlyhanie.

➡️ **Pri veľmi veľkých exportoch odporúčame lokálne spustenie** (`streamlit run app.py`).

---

## Ochrana zdravotných dát

✓ Všetky výpočty prebiehajú lokálne v pamäti session  
✓ Žiadne dáta nie sú odosielané na externé servery  
✓ Identifikátory zariadení sú anonymizované (subjekt_01, subjekt_02…)  
✓ Streamlit telemetria je vypnutá (`gatherUsageStats = false`)



---

## Testovanie

```bash
pytest tests/                          # Vsetky testy
pytest tests/unit                      # Jednotkove testy
pytest --cov=health_dashboard
```

---

## Konfigurácia

| Premenná prostredia | Predvolená hodnota | Popis |
|---------------------|-------------------|-------|
| `HD_LOCAL_TZ` | `Europe/Bratislava` | IANA časové pásmo pre nočné skupiny |

---

## Štruktúra projektu

```
.
├── app.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── .streamlit/
│   └── config.toml
├── src/
│   └── health_dashboard/
│       ├── alignment/
│       ├── analytics/
│       ├── ingestion/
│       ├── ui/
│       │   └── charts/
│       └── config.py
└── tests/
    ├── data/
    ├── integration/
    └── unit/
```

---

