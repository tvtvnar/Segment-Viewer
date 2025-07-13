# dashboard.py
"""Основной многостраничный дашборд."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from helpers import vc_df, hide_idx

# ───────────────────────────  ЦВЕТОВЫЕ КОНСТАНТЫ  ──────────────────────────
COL_FEMALE    = "#FFB6C1"
COL_MALE      = "#4682B4"
COL_BOT       = "#7B9EA8"
COL_USER      = "#A3C9A8"
COL_SEGMENT   = "#C3B1E1"
COL_CITY      = "#E4C7A8"
COL_INTERESTS = "#79C7C5"
COL_MEDIAN    = "#E8A798"
DEV_COLORS    = {
    "WEB": "#B0C4DE",
    "WEB Mobile": "#D1BAC4",
    "IOS app": "#C1E1C1",
    "Android app": "#C1DDE8",
}
COL_BOTS_CITY = "#D1C4E9"

# ──────────────────────────  ОЖИДАЕМЫЕ КОЛОНКИ  ─────────────────────────
REQ_COLUMNS = {"segment", "Тип аккаунта", "Пол", "Лет", "Устройство визита в VK", "group_count", "VK ID"}

def _check(df: pd.DataFrame):
    missing = REQ_COLUMNS - set(df.columns)
    if missing:
        st.error("В исходном файле не хватает колонок: " + ", ".join(missing))
        st.stop()

# ─────────────────────────────  HELPERS  ────────────────────────────────
def metric(col, label, value, delta=None):
    with col:
        st.metric(label, value, delta)


def bar_base(df: pd.DataFrame, x: str, y: str, **kwargs):
    fig = px.bar(
        df,
        x=x,
        y=y,
        text_auto=".0s",
        height=380,
        labels={x: "", y: "Количество"},
        **kwargs,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    fig.update_traces(hovertemplate=f"{x}: %{{x}}<br>Количество: %{{y:,}}")
    return fig

# ───────────────────────────  DASHBOARD  ───────────────────────────────
def run_dashboard(df: pd.DataFrame):
    # Проверяем колонки
    _check(df)

    # Фильтры
    with st.expander("Фильтры", expanded=True):
        segments = sorted(df["segment"].dropna().unique())
        types    = df["Тип аккаунта"].unique()
        genders  = df["Пол"].dropna().unique()
        amin, amax = int(df["Лет"].min()), int(df["Лет"].max())
        s_seg = st.multiselect("Сегмент", segments, default=segments)
        s_type= st.multiselect("Тип аккаунта", types, default=types)
        s_sex = st.multiselect("Пол", genders, default=genders)
        age_range = st.slider("Возраст", amin, amax, (amin, amax), step=1)

    # Фильтруем данные
    data = df[
        df["segment"].isin(s_seg)
      & df["Тип аккаунта"].isin(s_type)
      & df["Пол"].isin(s_sex)
      & df["Лет"].between(*age_range)
    ]

    # Навигация по страницам
    page = st.sidebar.radio(
        "Страница", ["🏠 Обзор","🎯 Интересы","📊 Активность","🤖 Боты","📋 Группы","📑 Данные"]
    )
    st.sidebar.caption("© 2025 Segment Viewer")

    # 1. Обзор
    if page == "🏠 Обзор":
        c1, c2, c3, c4, c5 = st.columns(5)
        metric(c1, "Всего записей", len(data))
        metric(c2, "% ботов", f"{data['Тип аккаунта'].eq('бот').mean()*100:.0f}%")
        metric(c3, "Средний возраст", f"{data['Лет'].mean():.1f}")
        top_seg = data['segment'].mode()[0] if not data.empty else "—"
        metric(c4, "Топ-сегмент", top_seg)
        metric(c5, "Медиана подписок", int(data["group_count"].median()))

        st.subheader("⭐ TOP-5 сегментов")
        top5 = vc_df(data['segment'], top=5, x_name="Сегмент", y_name="Количество")
        fig1 = px.bar(top5, x="Сегмент", y="Количество", text="Количество",
                      color_discrete_sequence=[COL_SEGMENT], height=380)
        fig1.update_traces(textposition="inside")
        fig1.update_layout(margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig1, use_container_width=True)

        g1, g2 = st.columns(2)
        with g1:
            st.subheader("🧑‍🤝‍🧑 Пол")
            pie = px.pie(vc_df(data['Пол'], x_name="Пол", y_name="Количество"),
                         names='Пол', values='Количество', hole=0.4, height=350,
                         color_discrete_map={"женский":COL_FEMALE,"мужской":COL_MALE})
            pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(pie, use_container_width=True)
        with g2:
            st.subheader("📊 Гистограмма возраста")
            hist = px.histogram(data, x='Лет', nbins=10,
                                labels={'Лет':'Возраст','count':'Количество'},
                                height=350, color_discrete_sequence=[COL_MALE])
            hist.update_layout(margin=dict(l=10,r=10,t=40,b=10))
            hist.update_yaxes(title='Количество')
            st.plotly_chart(hist, use_container_width=True)

        st.subheader("🏙️ TOP-10 городов")
        cities = vc_df(data['РОДНОЙ ГОРОД'].str.lower().fillna('Неизвестно'),
                       top=10, x_name="ГородLower", y_name="Количество")
        cities['Город']=cities['ГородLower'].str.title()
        fig2=bar_base(cities.sort_values('Количество',ascending=False),
                      'Город','Количество',
                      color_discrete_sequence=[COL_CITY])
        mx=cities['Количество'].max()
        fig2.update_traces(textposition=["inside" if v==mx else "outside" for v in fig2.data[0].y])
        st.plotly_chart(fig2, use_container_width=True)

    # 2. Интересы
    elif page == "🎯 Интересы":
        st.subheader("📊 Размер сегментов")
        seg_cnt = vc_df(data['segment'], x_name="segment", y_name="Количество").sort_values('Количество',ascending=False)
        fig1=px.bar(seg_cnt, x='segment', y='Количество', text='Количество',
                    color_discrete_sequence=[COL_INTERESTS], height=420)
        fig1.update_traces(textposition=["outside" if v<=2 else "inside" for v in fig1.data[0].y])
        fig1.update_layout(margin=dict(l=10,r=10,t=40,b=10), xaxis_tickangle=-35)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("🧑‍🤝‍🧑 Распределение сегментов по полу")
        df_g=data.groupby(['segment','Пол'])['VK ID'].count().reset_index(name='count')
        fig_g=px.bar(df_g,x='segment',y='count',color='Пол',text='count',
                     color_discrete_map={"женский":COL_FEMALE,"мужской":COL_MALE},height=450)
        fig_g.update_traces(textposition="inside")
        fig_g.update_layout(margin=dict(l=10,r=10,t=60,b=30),legend=dict(orientation="h",y=1.1,x=0.5,xanchor="center",title=""))
        st.plotly_chart(fig_g, use_container_width=True)

        st.subheader("🤖 Доля ботов внутри сегмента")
        share=data.groupby(['segment','Тип аккаунта'])['VK ID'].count().unstack(fill_value=0)
        pct=share.div(share.sum(axis=1),axis=0).reset_index().melt(id_vars='segment',var_name='Тип аккаунта',value_name='Доля')
        fig3=px.bar(pct,x='segment',y='Доля',color='Тип аккаунта',text=pct['Доля'].apply(lambda v:f"{v:.0%}"),
                    color_discrete_map={"бот":COL_BOT,"пользователь":COL_USER},height=450)
        fig3.update_traces(hovertemplate="%{y:.0%}")
        fig3.update_layout(barmode='stack',margin=dict(l=10,r=10,t=60,b=30),legend=dict(orientation="h",y=1.1,x=0.5,xanchor="center",title=""))
        st.plotly_chart(fig3,use_container_width=True)

    # 3. Активность
    elif page == "📊 Активность":
        m1,m2=st.columns(2)
        metric(m1,"Среднее подписок",f"{data['group_count'].mean():.1f}")
        metric(m2,"Медиана подписок",int(data['group_count'].median()))

        st.subheader("🏅 Медиана подписок по сегментам (TOP-10)")
        med=data.groupby('segment')['group_count'].median().reset_index(name='Медиана').sort_values('Медиана',ascending=False).head(10)
        fig_med=bar_base(med,'segment','Медиана',color_discrete_sequence=[COL_MEDIAN])
        fig_med.update_traces(textposition=["inside" if v==med['Медиана'].max() else "outside" for v in med['Медиана']])
        st.plotly_chart(fig_med,use_container_width=True)

        st.subheader("🌡️ Медиана подписок: сегмент × тип аккаунта")
        hm=data.pivot_table(index='segment',columns='Тип аккаунта',values='group_count',aggfunc='median',fill_value=0)
        fig_hm=px.imshow(hm,labels=dict(x="Тип аккаунта",y="Сегмент",color="Медиана"),height=450,aspect="auto",color_continuous_scale="Blues")
        fig_hm.update_layout(margin=dict(l=80,r=10,t=40,b=80))
        st.plotly_chart(fig_hm,use_container_width=True)

    # 4. Боты
    elif page == "🤖 Боты":
        bots=data[data['Тип аккаунта']=='бот']
        p95b=df['group_count'].quantile(0.95)
        b1,b2,b3=st.columns(3)
        metric(b1,"Всего ботов",len(bots))
        metric(b2,"% ботов",f"{len(bots)/len(data)*100:.0f}%")
        metric(b3,"Медиана подписок (боты)",int(bots['group_count'].median()))

        st.subheader("👨‍👩‍👧‍👦 Пол ботов")
        pie2=px.pie(vc_df(bots['Пол'],x_name="Пол",y_name="Количество"),names='Пол',values='Количество',hole=0.4,height=350,color_discrete_map={"женский":COL_FEMALE,"мужской":COL_MALE})
        pie2.update_traces(textposition="inside",textinfo="percent+label")
        st.plotly_chart(pie2,use_container_width=True)

    # 5. Группы
    elif page == "📋 Группы":
        st.subheader("📋 Все группы и число подписчиков")
        group_cols=[c for c in data.columns if c.startswith('group_') and c.endswith('_name')]
        if not group_cols:
            st.info("Нет колонок group_*_name в данных.")
            return
        melted=data.melt(id_vars=['segment'],value_vars=group_cols,value_name='Группа').dropna(subset=['Группа']).assign(Группа=lambda d:d['Группа'].str.strip())
        cnts=melted['Группа'].value_counts().reset_index(name='Количество').rename(columns={'index':'Группа'}).sort_values('Количество',ascending=False)
        st.dataframe(cnts,use_container_width=True,hide_index=True)
        st.download_button("💾 Скачать CSV",cnts.to_csv(index=False).encode(),"groups_counts.csv","text/csv")

    # 6. Данные
    else:
        st.subheader("📑 Таблица фильтрованных данных")
        cols=df.columns.tolist()
        cols.remove('VK ID'); cols.remove('Тип аккаунта')
        order=['VK ID','Тип аккаунта']+cols
        st.dataframe(data[order],use_container_width=True,hide_index=True)
        st.download_button("💾 Скачать CSV",data[order].to_csv(index=False).encode(),"filtered_data.csv","text/csv")
