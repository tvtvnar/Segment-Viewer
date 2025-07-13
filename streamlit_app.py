import streamlit as st

# 1) Configure the page before any other Streamlit calls
st.set_page_config(page_title="Segment Viewer", layout="centered")

# 2) Global CSS styles (optional)
st.markdown(
    """
    <style>
    div.block-container { max-width: 100%!important; padding-top: 3rem; }
    body { background: linear-gradient(180deg,#0077FF 0%,#E9F4FF 100%); }
    section[data-testid="stFileUploader"] { margin-left: auto; margin-right: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3) Imports after page config
import pandas as pd
from dashboard import run_dashboard

# 4) Debug indicator (remove in production)
st.write("🚀 Streamlit_app.py запущен!")

# Column synonyms
ALIASES = {
    "segment": ["segment"],
    "Тип аккаунта": ["Тип аккаунта"],
    "Пол": ["Пол", "ПОЛ"],
    "Лет": ["Лет", "Возраст", "ЛЕТ"],
    "Устройство визита в VK": ["Устройство визита в VK", "УСТРОЙСТВО ВИЗИТА В ВК"],
}

@st.cache_data
def _read(upload):
    """Read .csv or .xlsx into a DataFrame"""
    if upload.name.lower().endswith(".csv"):
        return pd.read_csv(upload)
    return pd.read_excel(upload)


def _canon(df: pd.DataFrame):
    """Rename columns to canonical names and return missing list"""
    missing = []
    mapping = {}
    for canon, vars in ALIASES.items():
        for v in vars:
            if v in df.columns:
                mapping[v] = canon
                break
        else:
            missing.append(canon)
    return df.rename(columns=mapping), missing


def _home():
    st.markdown(
        "<h1 style='text-align:center;'>👋 Segment Viewer для маркетологов</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:1.1rem;'>Загрузите выгрузку <b>ВКонтакте</b> – получите интерактивный дашборд.</p>",
        unsafe_allow_html=True,
    )
    upload = st.file_uploader("Загрузите файл Excel/CSV", type=["xlsx", "csv"])
    if upload is None:
        st.info("📂 Пожалуйста, загрузите файл, чтобы продолжить…")
        return
    try:
        df = _read(upload)
    except Exception as e:
        st.error(f"Не удалось прочитать файл: {e}")
        return
    st.success(f"Файл: {df.shape[0]} строк / {df.shape[1]} столбцов")
    df, missing = _canon(df)
    if missing:
        st.error("Отсутствуют колонки: " + ", ".join(missing))
        return
    st.session_state.df = df
    st.experimental_rerun()

# Entry point
def main():
    if "df" not in st.session_state:
        _home()
    else:
        run_dashboard(st.session_state.df)

if __name__ == "__main__":
    main()
