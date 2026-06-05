import streamlit as st
from health_dashboard import IngestionReport


def render_empty_state(message: str) -> None:
    st.info(f"ℹ️ {message}")


def render_insufficient_data(
    nights_available: int, nights_required: int, metric: str
) -> None:
    st.warning(
        f"⚠️ **Nedostatok dát** pre {metric}: k dispozícii {nights_available} noc/nocí, "
        f"potrebných {nights_required}."
    )


def render_ingestion_report(reports: list[IngestionReport]) -> None:
    for report in reports:
        if report.rows_dropped_invalid > 0 or report.rows_dropped_out_of_range > 0:
            dropped = report.rows_dropped_invalid + report.rows_dropped_out_of_range
            st.info(
                f"✓ **{report.filename}**: Načítaných {report.rows_read} záznamov, "
                f"zahodených {dropped} neplatných."
            )
        else:
            st.success(f"✓ **{report.filename}**: Načítaných {report.rows_read} záznamov.")

        if report.unknown_stage_count > 0:
            st.warning(
                f"⚠️ {report.unknown_stage_count} neznámych hodnôt spánkovej fázy "
                "bolo zaradených do kategórie 'Other'."
            )


def render_oom_warning(report: IngestionReport) -> None:
        st.warning(
            f"⚠️ **Dataset bol zredukovaný:** Pôvodný súbor mal {report.original_row_count:,} záznamov. "
            f"Z výkonnostných dôvodov bolo ponechaných {500_000:,} záznamov (každý n-tý). "
            "Dlhodobé trendy sú zachované, niektoré krátkodobé vzory môžu byť menej presné."
        )
