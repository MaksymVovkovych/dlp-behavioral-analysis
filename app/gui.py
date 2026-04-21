import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime
import socket

def scan_local_databases():
    common_ports = {
        5432: "PostgreSQL",
        3306: "MySQL/MariaDB",
        1433: "MS SQL Server",
        27017: "MongoDB"
    }
    found_dbs = []
    
    st.sidebar.write("🔍 Сканування портів...")
    for port, name in common_ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                found_dbs.append({"Тип": name, "Порт": port, "Статус": "В мережі"})
    return found_dbs


# У sidebar додаємо кнопку сканування
if st.sidebar.button("🔎 Знайти активні БД"):
    databases = scan_local_databases()
    if databases:
        st.sidebar.success(f"Знайдено БД: {len(databases)}")
        st.sidebar.table(databases)
    else:
        st.sidebar.warning("Активних БД не знайдено")

# Налаштування сторінки
st.set_page_config(page_title="SentinelDB | Behavioral DLP", layout="wide")

st.title("🛡️ SentinelDB: Behavioral DLP Analyzer")
st.sidebar.header("Налаштування моніторингу")

# Шлях до логів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.normpath(os.path.join(BASE_DIR, "..", "db", "logs", "postgresql.log"))

def load_data():
    data = []
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(?:statement|execute.*?): (.*)'
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    data.append({
                        'Time': pd.to_datetime(match.group(1)),
                        'Query': match.group(2).strip()
                    })
    return pd.DataFrame(data)

# Головний екран
if st.sidebar.button("Оновити дані"):
    df = load_data()
    
    if not df.empty:
        # Аналіз аномалій (проста логіка для тесту)
        df['Diff'] = df['Time'].diff().dt.total_seconds()
        df['Status'] = df['Diff'].apply(lambda x: "⚠️ ATTACK" if x < 1.0 else "✅ OK")
        
        # Метрики
        col1, col2, col3 = st.columns(3)
        col1.metric("Всього запитів", len(df))
        col2.metric("Виявлено аномалій", len(df[df['Status'] == "⚠️ ATTACK"]))
        col3.metric("Захищено таблиць", 1) # Поки що одна users_private

        # Графік активності
        st.subheader("📈 Графік інтенсивності доступу")
        fig = px.histogram(df, x="Time", color="Status", 
                           color_discrete_map={"✅ OK": "blue", "⚠️ ATTACK": "red"},
                           nbins=30)
        st.plotly_chart(fig, use_container_width=True)

        # Таблиця логів
        st.subheader("📝 Журнал подій та аналіз поведінки")
        st.dataframe(df.sort_values(by='Time', ascending=False), use_container_width=True)
    else:
        st.error("Файл логів пустий або не знайдений. Запустіть базу та зробіть запити.")
        # Після відображення таблиці в Streamlit
    st.subheader("📊 Експорт результатів")
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Завантажити повний звіт (CSV)",
        data=csv,
        file_name=f"sentinel_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime='text/csv',
    )
else:
    st.info("Натисніть 'Оновити дані' для початку аналізу активності БД.")


from sklearn.ensemble import IsolationForest

def calculate_ml_threat(df):
    if len(df) < 5:  # Мало даних для навчання
        return df, 0
    
    # Готуємо ознаки (features)
    df['hour'] = df['Time'].dt.hour
    df['query_len'] = df['Query'].str.len()
    df['is_select'] = df['Query'].str.upper().str.contains('SELECT').astype(int)
    
    # Навчаємо модель "на льоту"
    model = IsolationForest(contamination=0.1, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[['hour', 'query_len', 'is_select']])
    
    # Рахуємо % аномалій
    threat_level = int((df['anomaly_score'] == -1).mean() * 100)
    return df, threat_level




