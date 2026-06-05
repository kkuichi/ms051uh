from io import BytesIO
import streamlit as st


def render_upload_panel() -> tuple[BytesIO | None, BytesIO | None]:
    st.sidebar.markdown("## Upload Health Data")

    st.sidebar.markdown(
        """
    Upload CSV exports from Apple Health app:
    - **Heart rate**: Semicolon-separated; columns: `id`, `value`, `unit`, `startDate`
    - **Sleep**: Semicolon-separated; columns: `id`, `value`, `startDate`, `endDate`
    """
    )

    hr_file = st.sidebar.file_uploader(
        "Heart rate CSV",
        type=["csv"],
        key="hr_upload",
        accept_multiple_files=False,
    )

    sleep_file = st.sidebar.file_uploader(
        "Sleep CSV",
        type=["csv"],
        key="sleep_upload",
        accept_multiple_files=False,
    )

    hr_buf = None
    sleep_buf = None

    if hr_file is not None:
        hr_buf = BytesIO(hr_file.read())
        hr_buf.seek(0)

    if sleep_file is not None:
        sleep_buf = BytesIO(sleep_file.read())
        sleep_buf.seek(0)

    return hr_buf, sleep_buf