# app.py
"""Старт: загрузить файл, нормализовать колонки и вызвать дашборд."""
import streamlit as st, pandas as pd
from dashboard import run_dashboard

st.set_page_config(page_title="Segment Viewer",layout="centered")
st.markdown("""
<style>
div.block-container{max-width:100%!important; padding-top:3rem;}
body{background:linear-gradient(180deg,#0077FF 0%,#E9F4FF 100%);}
section[data-testid="stFileUploader"]{margin-left:auto;margin-right:auto;}
</style>""",unsafe_allow_html=True)

# ---- синонимы колонок ----
ALIASES = {
 "segment":["segment"],
 "Тип аккаунта":["Тип аккаунта"],
 "Пол":["Пол","ПОЛ"],
 "Лет":["Лет","Возраст","ЛЕТ"],
 "Устройство визита в VK":["Устройство визита в VK","УСТРОЙСТВО ВИЗИТА В ВК"],
}
def _read(upload):
    return pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)

def _canon(df):
    miss=[]; mapping={}
    for canon,vars in ALIASES.items():
        for v in vars:
            if v in df.columns: mapping[v]=canon; break
        else: miss.append(canon)
    return df.rename(columns=mapping),miss

def _home():
    st.markdown("<h1 style='text-align:center;'>👋 Segment Viewer для маркетологов</h1>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.1rem;'>Загрузите выгрузку <b>ВКонтакте</b> – получите интерактивный дашборд.</p>",unsafe_allow_html=True)
    up=st.file_uploader("Загрузите файл Excel/CSV",type=["xlsx","csv"])
    if up is None:
        st.info("📂 Пожалуйста, загрузите файл, чтобы продолжить…"); return
    try: df=_read(up)
    except Exception as e: st.error(f"Не прочитал файл: {e}"); return
    st.success(f"Файл: {df.shape[0]} строк / {df.shape[1]} столбцов")
    df,miss=_canon(df)
    if miss: st.error("Отсутствуют колонки: "+", ".join(miss)); return
    st.session_state.df=df; st.rerun()

if "df" not in st.session_state:
    _home()
else:
    run_dashboard(st.session_state.df)