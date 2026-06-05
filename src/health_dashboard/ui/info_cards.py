from __future__ import annotations
import streamlit as st


_MODALS: dict[str, dict] = {
    "privacy": {
        "icon": "🔒",
        "badge": "Spracovanie dát",
        "title": "Ochrana dát a súkromia",
        "body": (
            "Nahrané zdravotné dáta sa spracúvajú <strong>iba počas aktuálnej "
            "session</strong> aplikácie na účely analýzy a vizualizácie. "
            "Aplikácia ich zámerne neukladá do databázy ani ich ďalej nezdieľa. "
            "Keďže aplikácia beží na <strong>Streamlit Cloud</strong>, dáta sa "
            "počas spracovania môžu dočasne nachádzať v pamäti servera."
            "<ul>"
            "<li>Osobné identifikátory sú automaticky anonymizované "
            "na kódy <em>subjekt_01</em>, <em>subjekt_02</em>&nbsp;…</li>"
            "<li>Po skončení session sú dáta vymazané — nič sa trvalo neukladá</li>"
            "<li>Streamlit telemetria je v tejto aplikácii vypnutá</li>"
            "</ul>"
        ),
    },
    "science": {
        "icon": "🧪",
        "badge": "Odborné pozadie metrík",
        "title": "Vedecké okienko",
        "body": (
            "Aplikácia obsahuje <strong>detailné vedecké vysvetlenia</strong> "
            "grafov, metrík a analytických výsledkov vhodné aj pre bakalársku prácu."
            "<ul>"
            "<li>Pri každom grafe kliknite na "
            "<em>🔬 Vedecké vysvetlenie grafu</em> pre fyziologické súvislosti</li>"
            "<li>Pri tabuľke nájdete <em>📘 Vysvetlenie pojmov</em> "
            "(mean, std, bpm, NaN&nbsp;…)</li>"
            "<li>Sekcia <em>🔬 Vedecké okienko</em> na konci stránky obsahuje "
            "referenčné hodnoty, literatúru a metodologické obmedzenia</li>"
            "</ul>"
            "Všetky výsledky sú <strong>orientačné</strong> — podporný "
            "vizualizačný nástroj, nie medicínska diagnostika."
        ),
    },
    "xml": {
        "icon": "ℹ️",
        "badge": "Odporúčania pre import",
        "title": "Apple Health XML – tipy",
        "body": (
            "Apple Health XML exporty môžu byť pri viacročnom používaní "
            "<strong>veľmi veľké</strong> (stovky MB až niekoľko GB)."
            "<ul>"
            "<li><strong>Lokálne spustenie</strong> "
            "(<code>streamlit run app.py</code>) zvláda aj súbory nad 1&nbsp;GB</li>"
            "<li>Streamlit Cloud je obmedzený RAM a timeoutom — "
            "odporúčame súbory do 200&nbsp;MB</li>"
            "<li>Aplikácia streamuje XML sekvenčne — spotreba pamäte je "
            "konštantná ~40–50&nbsp;MB bez ohľadu na veľkosť súboru</li>"
            "<li>Export: <em>Apple Zdravie → Profil → Exportovať zdravotné dáta</em></li>"
            "</ul>"
            "Alternatívne použite <strong>CSV páry</strong> "
            "(<code>demo_heartrate.csv</code> + <code>demo_sleep.csv</code>) "
            "na rýchle otestovanie aplikácie."
        ),
    },
}


_CSS = """
<style>
.ic-card {
    background: linear-gradient(135deg, rgba(30,58,95,.72) 0%, rgba(20,40,70,.60) 100%);
    border: 1px solid rgba(78,121,167,.35);
    border-radius: 14px;
    padding: 14px 16px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 2px 16px rgba(0,0,0,.18);
    user-select: none;
    pointer-events: none;
    margin-bottom: 6px;
}
.ic-icon  { font-size: 22px; display: block; margin-bottom: 6px; }
.ic-title { font-size: 13px; font-weight: 600; color: #c8dff5;
            letter-spacing: .02em; margin: 0; }
.ic-hint  { font-size: 11px; color: rgba(160,195,230,.65); margin-top: 3px; }

.hd-modal {
    background: linear-gradient(145deg, rgba(18,42,76,.97) 0%, rgba(10,28,54,.99) 100%);
    border: 1px solid rgba(78,121,167,.50);
    border-radius: 20px;
    padding: 28px 30px 24px;
    box-shadow: 0 24px 60px rgba(0,0,0,.55),
                0 0 0 1px rgba(100,160,220,.12) inset;
    margin: 8px 0 12px;
}
.hd-modal-icon  { font-size: 32px; display: block; margin-bottom: 9px; }
.hd-modal-badge {
    display: inline-block;
    background: rgba(78,121,167,.22);
    border: 1px solid rgba(78,121,167,.42);
    border-radius: 6px;
    padding: 2px 9px;
    font-size: 11px;
    color: #90c0f0;
    margin-bottom: 13px;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.hd-modal-title {
    font-size: 17px; font-weight: 700;
    color: #d0e8ff; margin-bottom: 12px;
    letter-spacing: .01em;
}
.hd-modal-body {
    font-size: 13.5px;
    color: rgba(190,215,245,.88);
    line-height: 1.68;
}
.hd-modal-body strong { color: #a8d4ff; font-weight: 600; }
.hd-modal-body em     { color: rgba(180,210,245,.80); font-style: italic; }
.hd-modal-body code   {
    font-family: 'SF Mono','Fira Code', monospace;
    font-size: 12px;
    background: rgba(78,121,167,.22);
    border-radius: 4px;
    padding: 1px 5px;
    color: #90c0f0;
}
.hd-modal-body ul { padding-left: 18px; margin: 9px 0 0; }
.hd-modal-body li { margin-bottom: 6px; }
.hd-modal-divider {
    border: none;
    border-top: 1px solid rgba(78,121,167,.22);
    margin: 18px 0 14px;
}
</style>
"""


def _card_html(icon: str, title: str, hint: str) -> str:
    return (
        f'<div class="ic-card">'
        f'<span class="ic-icon">{icon}</span>'
        f'<p class="ic-title">{title}</p>'
        f'<p class="ic-hint">{hint}</p>'
        f'</div>'
    )


def _modal_html(key: str) -> str:
    m = _MODALS[key]
    return (
        f'<div class="hd-modal">'
        f'<span class="hd-modal-icon">{m["icon"]}</span>'
        f'<span class="hd-modal-badge">{m["badge"]}</span>'
        f'<p class="hd-modal-title">{m["title"]}</p>'
        f'<div class="hd-modal-body">{m["body"]}</div>'
        f'<hr class="hd-modal-divider">'
        f'</div>'
    )


def render_info_cards() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    if "active_modal" not in st.session_state:
        st.session_state.active_modal = None

    card_defs = [
        ("privacy", "🔒", "Ochrana dát", "Ako nakladáme s vašimi dátami"),
        ("science", "🧪", "Vedecké okienko", "Odborné pozadie grafov a metrík"),
        ("xml", "ℹ️", "Apple Health XML", "Tipy pre import a veľké exporty"),
    ]

    cols = st.columns(3)
    for col, (key, icon, title, hint) in zip(cols, card_defs):
        with col:
            st.markdown(_card_html(icon, title, hint), unsafe_allow_html=True)
            if st.button(
                f"{icon}  {title}",
                key=f"ic_btn_{key}",
                help=hint,
                use_container_width=True,
            ):
                st.session_state.active_modal = (
                    None if st.session_state.active_modal == key else key
                )

    active = st.session_state.active_modal
    if active and active in _MODALS:
        st.markdown(_modal_html(active), unsafe_allow_html=True)
        if st.button("Zavrieť", key="hd_modal_close", use_container_width=False):
            st.session_state.active_modal = None
            st.rerun()