import os
import re
from datetime import datetime

# Автоматичне визначення шляху до файлу логів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.normpath(os.path.join(BASE_DIR, "..", "db", "logs", "postgresql.log"))

def analyze_behavior():
    if not os.path.exists(LOG_FILE):
        print(f"❌ Файл не знайдено: {LOG_FILE}")
        return

    # Оновлений шаблон: шукає АБО statement, АБО execute
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(?:statement|execute.*?): (.*)'
    
    last_time = None
    
    print(f"{'СТАТУС':<12} | {'ЧАС':<20} | {'SQL ЗАПИТ'}")
    print("-" * 80)

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                current_time_str = match.group(1)
                query = match.group(2).strip()
                
                # Фільтруємо технічні запити (BEGIN, COMMIT) і фокусуємось на таблциі
                if "users_private" in query:
                    # Перетворюємо текст у об'єкт часу для математичних розрахунків
                    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
                    
                    status = "OK"
                    if last_time:
                        diff = (current_time - last_time).total_seconds()
                        # Хакер зазвичай діє швидше ніж 1 запит на секунду
                        if diff < 1.0: 
                            status = "⚠️ ATTACK"
                    
                    print(f"{status:<12} | {current_time_str:<20} | {query[:40]}...")
                    last_time = current_time

if __name__ == "__main__":
    analyze_behavior()