import streamlit as st
import engine # Імпортуємо нашу логіку
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SentinelDB | Hybrid Audit", layout="wide")
st.title("🛡️ SentinelDB: Behavioral DLP System")

# --- СІДЕБАР (Discovery) ---
st.sidebar.header("🔍 Система виявлення")
if st.sidebar.button("Сканувати локальні БД"):
    dbs = engine.scan_local_databases()
    if dbs:
        st.sidebar.success(f"Знайдено: {len(dbs)}")
        st.sidebar.table(dbs)
    else:
        st.sidebar.warning("БД не знайдено")

# --- ГОЛОВНІ ВКЛАДКИ ---
tab_logs, tab_sys, tab_live = st.tabs([
    "📄 Аналіз логів (Forensic)", 
    "🔑 Системний аудит (Privileged)", 
    "📡 Live Трафік (Network)"
])

# --- ВКЛАДКА 1: ЛОГИ ---
with tab_logs:
    if st.button("🚀 Run Deep ML Analysis"):
        df = engine.load_logs()
        df, threat_level = engine.analyze_data(df)

        if not df.empty:
            # Створюємо колонки для статистики
            col_metrics, col_chart = st.columns([1, 1])

            with col_metrics:
                st.metric("Global Threat Level", f"{threat_level}%", delta=f"{threat_level}% risk", delta_color="inverse")
                st.write(f"📊 Всього оброблено запитів: **{len(df)}**")
                st.write(f"🚨 Виявлено аномалій: **{len(df[df['Status'] == '⚠️ ATTACK'])}**")

            with col_chart:
                # МАЛЮЄМО КРУЖОЧОК (Pie Chart)
                fig = px.pie(df, names='Status', title='Розподіл безпеки запитів',
                             color='Status', color_discrete_map={'✅ OK':'#2ecc71', '⚠️ ATTACK':'#e74c3c'},
                             hole=0.4) # Робимо його "бубликом"
                st.plotly_chart(fig, use_container_width=True)
                
            st.subheader("📊 Експорт результатів")
            csv = df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📥 Завантажити повний звіт (CSV)",
                data=csv,
                file_name=f"sentinel_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv',
            )

            # ГРАФІК ЧАСОВОЇ АКТИВНОСТІ
            st.subheader("📈 Хронологія активності")
            line_fig = px.scatter(df, x="Time", y="query_len", color="Status",
                                  title="Залежність довжини запиту від часу",
                                  color_discrete_map={'✅ OK':'#2ecc71', '⚠️ ATTACK':'#e74c3c'})
            st.plotly_chart(line_fig, use_container_width=True)

            # ТАБЛИЦЯ
            st.subheader("📝 Детальний лог аномалій")
            st.dataframe(df.sort_values(by='Time', ascending=False), use_container_width=True)


        else:
            st.error("Дані відсутні.")

# --- ВКЛАДКА 2: SQL АУДИТ ---
with tab_sys:
    st.header("Опитування активних сесій (pg_stat_activity)")
    st.info("Цей метод дозволяє бачити запити в пам'яті без доступу до файлів.")
    if st.button("Зняти дамп активності"):
        st.warning("Потрібні облікові дані адміністратора БД.")

# --- ВКЛАДКА 3: LIVE ТРАФІК ---
with tab_live:
    st.header("Мережевий сніффер")
    st.write("Перехоплення пакетів на порту 5432.")
    if st.button("Запустити Live моніторинг"):
        st.error("Потрібні права Root/Admin та встановлений Npcap/Libpcap.")