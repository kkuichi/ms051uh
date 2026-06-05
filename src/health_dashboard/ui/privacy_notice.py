import streamlit as st


def render_privacy_notice() -> None:
    if "privacy_notice_shown" not in st.session_state:
        st.session_state.privacy_notice_shown = False

    if not st.session_state.privacy_notice_shown:
        st.info(
            "🔒 **Ochrana dát a súkromia**\n\n"
            "Vaše zdravotné dáta sú spracovávané výhradne v pamäti tejto session. "
            "**Žiadne dáta nie sú odosielané na externé servery ani ukladané na disk.** "
            "Všetka analýza prebieha lokálne, v reálnom čase. "
            "Osobné identifikátory (meno zariadenia) sú automaticky anonymizované."
        )
        st.session_state.privacy_notice_shown = True
