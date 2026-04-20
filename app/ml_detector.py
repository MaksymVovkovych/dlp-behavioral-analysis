import pandas as pd
import re
import os
from sklearn.ensemble import IsolationForest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.normpath(os.path.join(BASE_DIR, "..", "db", "logs", "postgresql.log"))

def prepare_data():
    data = []
    # Регулярка для витягування часу та SQL
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(?:statement|execute.*?): (.*)'
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                ts = pd.to_datetime(match.group(1))
                query = match.group(2).strip()
                
                # Створюємо ознаки (Features) для ML:
                data.append({
                    'hour': ts.hour,
                    'query_len': len(query),
                    'special_chars': sum(1 for c in query if c in "';*--="), # Ознаки SQL-ін'єкцій або складних запитів
                    'is_select': 1 if "SELECT" in query.upper() else 0
                })
    return pd.DataFrame(data)

def run_ml_detection():
    df = prepare_data()
    if df.empty: return

    # Налаштовуємо модель Isolation Forest
    # contamination=0.05 означає, що ми очікуємо ~5% аномалій
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Навчаємо модель на наших ознаках
    df['anomaly_score'] = model.fit_predict(df[['hour', 'query_len', 'special_chars', 'is_select']])
    
    # -1 означає аномалію, 1 - нормальну поведінку
    anomalies = df[df['anomaly_score'] == -1]

    print(f"🤖 ML Аналіз завершено. Оброблено запитів: {len(df)}")
    print(f"🚨 Виявлено підозрілих аномалій: {len(anomalies)}")
    
    if not anomalies.empty:
        print("\n--- Топ підозрілих активностей ---")
        print(anomalies.head())

if __name__ == "__main__":
    run_ml_detection()