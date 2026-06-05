from __future__ import annotations

import os
from io import BytesIO

import pandas as pd
import streamlit as st

from health_dashboard.config import LOCAL_TZ
from health_dashboard.ingestion.anonymizer import (
    anonymize_dataframe,
    build_subject_mapping,
    inject_placeholder_source,
)
from health_dashboard.ingestion.exporter import (
    build_hr_export_df,
    build_sleep_export_df,
    dataframe_to_csv_bytes,
    subject_csv_filename,
)
from health_dashboard.ingestion.xml_parser import (
    STREAMLIT_DEFAULT_UPLOAD_LIMIT_MB,
    parse_apple_health_xml,
    save_upload_to_tempfile,
)


_LARGE_FILE_WARNING = (
    f"ℹ️ **Veľké XML súbory:** Apple Health exporty môžu presiahnuť "
    f"{STREAMLIT_DEFAULT_UPLOAD_LIMIT_MB} MB. "
    "Pri dlhodobej histórii (3+ roky) môže byť vhodnejšie lokálne spustenie."
)

_UPLOAD_LIMIT_ERROR = """\
❌ **Súbor je príliš veľký pre aktuálny upload limit.**

**Možnosti riešenia:**

1. **Lokálne spustenie**:

2. **Exportujte kratšie časové obdobie** z Apple Health.

3. **Použite CSV súbory.**
"""

_XML_HOW_TO = """\
**Ako exportovať z Apple Health:**
1. Otvorte aplikáciu **Zdravie**
2. Kliknite na profil
3. Zvoľte **Exportovať všetky zdravotné dáta**
4. Rozbaľte ZIP archív
5. Nahrajte súbor `export.xml`
"""


def _parse_csv_uploads(
 hr_file,
 sleep_file,
 local_tz: str,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
 from health_dashboard.ingestion.csv_parser import parse_heart_rate, parse_sleep

 hr_df = sleep_df = None

 if hr_file is not None:
     try:
         buf = BytesIO(hr_file.read())
         hr_raw, hr_report = parse_heart_rate(
             buf,
             filename=hr_file.name,
             local_tz=local_tz,
         )
         hr_raw = inject_placeholder_source(hr_raw)
         mapping = build_subject_mapping(hr_raw["source_raw"])
         hr_df = anonymize_dataframe(hr_raw, mapping)

         st.sidebar.success(
             f"✅ HR: {hr_report.rows_read} záznamov načítaných"
             + (
                 f", {hr_report.rows_dropped_invalid} zahodených"
                 if hr_report.rows_dropped_invalid
                 else ""
             )
         )
     except Exception as exc:
         st.sidebar.error(f"❌ Chyba HR CSV: {exc}")

 if sleep_file is not None:
     try:
         buf = BytesIO(sleep_file.read())
         sleep_raw, sleep_report = parse_sleep(
             buf,
             filename=sleep_file.name,
             local_tz=local_tz,
         )
         sleep_raw = inject_placeholder_source(sleep_raw)
         mapping = build_subject_mapping(sleep_raw["source_raw"])
         sleep_df = anonymize_dataframe(sleep_raw, mapping)

         st.sidebar.success(
             f"✅ Spánok: {sleep_report.rows_read} záznamov načítaných"
             + (
                 f", {sleep_report.rows_dropped_invalid} zahodených"
                 if sleep_report.rows_dropped_invalid
                 else ""
             )
         )
     except Exception as exc:
         st.sidebar.error(f"❌ Chyba Sleep CSV: {exc}")

 return hr_df, sleep_df


def _parse_xml_upload(
 xml_file,
 local_tz: str,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
 tmp_path: str | None = None

 try:
     file_size_mb = _get_uploaded_file_size_mb(xml_file)
     size_label = f"{file_size_mb:.0f} MB" if file_size_mb else "neznáma veľkosť"

     with st.spinner(f"Nahrávam XML ({size_label}) na spracovanie…"):
         tmp_path = save_upload_to_tempfile(xml_file)

     actual_mb = os.path.getsize(tmp_path) / (1024 * 1024)
     st.info(f"📂 Súbor uložený: {actual_mb:.1f} MB – spúšťam parsovanie…")

     with st.spinner("Extrahujem záznamy z XML…"):
         hr_df, sleep_df, hr_report, sleep_report = parse_apple_health_xml(
             tmp_path,
             local_tz=local_tz,
         )

 except Exception as exc:
     err_str = str(exc).lower()

     if any(kw in err_str for kw in ("too large", "size", "limit", "exceed", "413")):
         st.error(_UPLOAD_LIMIT_ERROR)
     else:
         st.error(f"❌ Chyba pri spracovaní XML: {exc}")

     return None, None

 finally:
     if tmp_path and os.path.exists(tmp_path):
         try:
             os.unlink(tmp_path)
         except OSError:
             pass

 if hr_df is None and sleep_df is None:
     st.error(
         "❌ V nahranom XML neboli nájdené žiadne záznamy "
         "srdcovej frekvencie ani spánku."
     )
     return None, None

 _render_parse_results(hr_df, sleep_df, hr_report, sleep_report)
 hr_df, sleep_df = _anonymize_xml_data(hr_df, sleep_df)

 if hr_df is not None or sleep_df is not None:
     _render_xml_export_buttons(hr_df, sleep_df)

 return hr_df, sleep_df


def _get_uploaded_file_size_mb(uploaded_file) -> float | None:
 try:
     if hasattr(uploaded_file, "size"):
         return uploaded_file.size / (1024 * 1024)
 except Exception:
     pass

 return None


def _render_parse_results(hr_df, sleep_df, hr_report, sleep_report) -> None:
 cols = st.columns(2)

 with cols[0]:
     if hr_df is not None and hr_report is not None:
         delta = (
             hr_report.rows_dropped_invalid
             + hr_report.rows_dropped_out_of_range
         )

         st.success(
             f"✅ **Srdcová frekvencia**\n\n"
             f"Načítaných: **{hr_report.rows_read:,}** záznamov"
             + (f"\nZahodených: {delta}" if delta else "")
             + (
                 "\n⚠️ Dáta boli zredukované z dôvodu veľkosti."
                 if hr_report.was_downsampled
                 else ""
             )
         )
     else:
         st.warning("⚠️ Záznamy srdcovej frekvencie neboli nájdené.")

 with cols[1]:
     if sleep_df is not None and sleep_report is not None:
         st.success(
             f"✅ **Spánok**\n\n"
             f"Načítaných: **{sleep_report.rows_read:,}** záznamov"
             + (
                 f"\nZahodených: {sleep_report.rows_dropped_invalid}"
                 if sleep_report.rows_dropped_invalid
                 else ""
             )
             + (
                 f"\nNeznáme fázy: {sleep_report.unknown_stage_count}"
                 if sleep_report.unknown_stage_count
                 else ""
             )
         )
     else:
         st.warning("⚠️ Záznamy spánku neboli nájdené.")


def _anonymize_xml_data(
 hr_df: pd.DataFrame | None,
 sleep_df: pd.DataFrame | None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
 sources = []

 if hr_df is not None and "source_raw" in hr_df.columns:
     sources.append(hr_df["source_raw"])

 if sleep_df is not None and "source_raw" in sleep_df.columns:
     sources.append(sleep_df["source_raw"])

 if not sources:
     if hr_df is not None:
         hr_df = inject_placeholder_source(hr_df)
         hr_df = anonymize_dataframe(hr_df, {"csv_upload": "subjekt_01"})

     if sleep_df is not None:
         sleep_df = inject_placeholder_source(sleep_df)
         sleep_df = anonymize_dataframe(sleep_df, {"csv_upload": "subjekt_01"})

     return hr_df, sleep_df

 mapping = build_subject_mapping(*sources)
 n = len(mapping)

 st.info(
     f"🔒 **Anonymizácia:** Identifikovaných {n} "
     f"{'identifikátor' if n == 1 else 'identifikátory'} zdrojov → "
     f"nahradené kódmi subjekt_01"
     + (f" … subjekt_{n:02d}" if n > 1 else "")
     + "."
 )

 if hr_df is not None:
     hr_df = anonymize_dataframe(hr_df, mapping)

 if sleep_df is not None:
     sleep_df = anonymize_dataframe(sleep_df, mapping)

 return hr_df, sleep_df


def _render_xml_export_buttons(
 hr_df: pd.DataFrame | None,
 sleep_df: pd.DataFrame | None,
) -> None:
 st.markdown("#### 📥 Stiahnutie extrahovaných dát ako CSV")
 st.caption("Exportované súbory sú anonymizované a pripravené na ďalšiu analýzu.")

 col1, col2 = st.columns(2)

 if hr_df is not None:
     subjects = (
         sorted(hr_df["subject_id"].unique().tolist())
         if "subject_id" in hr_df.columns
         else ["subjekt_01"]
     )

     export_df = build_hr_export_df(hr_df)
     fname = subject_csv_filename("heart_rate", subjects)

     col1.download_button(
         label="⬇️ Srdcová frekvencia CSV",
         data=dataframe_to_csv_bytes(export_df),
         file_name=fname,
         mime="text/csv",
         help=f"Stiahne {len(export_df):,} anonymizovaných HR záznamov.",
     )
     col1.caption(f"`{fname}` · {len(export_df):,} riadkov")

 if sleep_df is not None:
     subjects = (
         sorted(sleep_df["subject_id"].unique().tolist())
         if "subject_id" in sleep_df.columns
         else ["subjekt_01"]
     )

     export_df = build_sleep_export_df(sleep_df)
     fname = subject_csv_filename("sleep", subjects)

     col2.download_button(
         label="⬇️ Spánok CSV",
         data=dataframe_to_csv_bytes(export_df),
         file_name=fname,
         mime="text/csv",
         help=f"Stiahne {len(export_df):,} anonymizovaných sleep záznamov.",
     )
     col2.caption(f"`{fname}` · {len(export_df):,} riadkov")


def render_upload_panel(
 local_tz: str = LOCAL_TZ,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
 st.sidebar.markdown("## 📂 Nahrať zdravotné dáta")

 input_mode = st.sidebar.radio(
     "Formát vstupu",
     options=["CSV súbory", "Apple Health XML"],
     index=0,
     help=(
         "**CSV:** Nahrajte dva oddelené súbory.\n\n"
         "**XML:** Nahrajte export.xml priamo z Apple Health."
     ),
 )

 if input_mode == "CSV súbory":
     st.sidebar.markdown(
         "**Formát:**\n"
         "- HR: `id; value; unit; startDate`\n"
         "- Sleep: `id; value; startDate; endDate`\n\n"
         "📁 Testovacie súbory nájdete v priečinku `tests/data/`."
     )

     hr_file = st.sidebar.file_uploader(
         "Srdcová frekvencia (CSV)",
         type=["csv"],
         key="hr_csv_upload",
     )

     sleep_file = st.sidebar.file_uploader(
         "Spánok (CSV)",
         type=["csv"],
         key="sleep_csv_upload",
     )

     if hr_file is None and sleep_file is None:
         st.sidebar.info("Nahrajte oba CSV súbory pre spustenie analýzy.")
         return None, None

     return _parse_csv_uploads(hr_file, sleep_file, local_tz)

 st.sidebar.warning(_LARGE_FILE_WARNING)

 with st.sidebar.expander("ℹ️ Ako exportovať z Apple Health"):
     st.markdown(_XML_HOW_TO)

 xml_file = st.sidebar.file_uploader(
     "Apple Health export.xml",
     type=["xml"],
     key="xml_upload",
     help=(
         f"Maximálna veľkosť závisí od nastavenia server.maxUploadSize "
         f"(aktuálne {STREAMLIT_DEFAULT_UPLOAD_LIMIT_MB} MB)."
     ),
 )

 if xml_file is None:
     st.sidebar.info("Nahrajte súbor export.xml z Apple Health.")
     return None, None

 file_mb = _get_uploaded_file_size_mb(xml_file)

 if file_mb and file_mb > 100:
     st.info(
         f"📊 Nahrávate veľký súbor ({file_mb:.0f} MB). "
         "Spracovanie môže chvíľu trvať."
     )

 return _parse_xml_upload(xml_file, local_tz)