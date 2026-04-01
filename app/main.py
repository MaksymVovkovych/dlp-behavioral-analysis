import os
import re
from datetime import datetime

LOG_FILE = os.path.join("..", "db", "logs", "postgresql.log")

def analyze_behavior():
    if not os.path.exists(LOG_FILE):
        return

    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*execute <unnamed>: (.*)'
    
    last_time = None
    
    print(f"{'СТАТУС':<12} | {'ЧАС':<20} | {'SQL ЗАПИТ'}")
    print("-" * 80)

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                current_time_str = match.group(1)
                query = match.group(2).strip()
                
                # Тільки якщо це запит до нашої секретної таблиці
                if "users_private" in query:
                    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
                    
                    status = "OK"
                    # Якщо це не перший запит, рахуємо різницю в часі
                    if last_time:
                        diff = (current_time - last_time).total_seconds()
                        if diff < 1.0: # Поріг 1 секунда
                            status = "⚠️ ATTACK"
                    
                    print(f"{status:<12} | {current_time_str:<20} | {query[:40]}...")
                    last_time = current_time

if __name__ == "__main__":
    analyze_behavior()