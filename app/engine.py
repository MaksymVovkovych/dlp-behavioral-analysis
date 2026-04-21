import os
import re
import socket
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest

# Універсальний шлях до логів
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "db" / "logs" / "postgresql.log"

def scan_local_databases():
    common_ports = {5432: "PostgreSQL", 3306: "MySQL", 1433: "MS SQL", 27017: "MongoDB"}
    found_dbs = []
    for port, name in common_ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                found_dbs.append({"Тип": name, "Порт": port, "Статус": "Active"})
    return found_dbs

def load_logs():
    data = []
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(?:statement|execute.*?): (.*)'
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    data.append({'Time': pd.to_datetime(match.group(1)), 'Query': match.group(2).strip()})
    return pd.DataFrame(data)

def analyze_data(df):
    if df.empty or len(df) < 5:
        if not df.empty:
            df['Status'] = "✅ OK"
            df['Risk_Score'] = 0.05
        return df, 0

    # ФІЧІ ДЛЯ ML (робимо модель розумнішою)
    df['hour'] = df['Time'].dt.hour
    df['sec_diff'] = df['Time'].diff().dt.total_seconds().fillna(0)
    df['query_len'] = df['Query'].str.len()
    # Важливі слова для SQL ін'єкцій
    df['is_danger'] = df['Query'].str.upper().str.contains('UNION|SELECT|DROP|OR 1=1|--').astype(int)
    
    # Навчання моделі
    model = IsolationForest(contamination=0.1, random_state=42)
    # anomaly_score: -1 це аномалія, 1 це норма
    preds = model.fit_predict(df[['hour', 'sec_diff', 'query_len', 'is_danger']])
    
    df['Status'] = np.where(preds == -1, "⚠️ ATTACK", "✅ OK")
    
    # Розрахунок загального рівня загрози (0-100%)
    threat_percent = int((df['Status'] == "⚠️ ATTACK").mean() * 100)
    
    return df, threat_percent

# Функція-заглушка для майбутнього сніффера (будемо наповнювати далі)
def get_live_traffic():
    return pd.DataFrame(columns=['Time', 'Source', 'Query', 'Risk'])