import psycopg2 # Треба буде встановити: pip install psycopg2-binary
import time
import random 

def simulate_leak():
    try:
        # Підключаємося до твоєї бази в Docker
        conn = psycopg2.connect(
            dbname="dlp_audit",
            user="admin",
            password="password123",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        
        print("🚀 Початок атаки: Ексфільтрація даних через ітераційні запити...")
        # Атака: витягуємо дані порціями, імітуючи "пошук", але насправді зливаємо все
        for i in range(1, 1001, 5):
            query = f"SELECT * FROM clients WHERE id BETWEEN {i} AND {i+4};"
            cur.execute(query)
            data = cur.fetchall()
            
            # Імітуємо випадкові паузи, щоб обійти прості ліміти (Throttling)
            time.sleep(random.uniform(0.1, 0.5)) 
            
            if i % 100 == 1:
                print(f"📡 Злито {i} записів...")

        print("✅ Атака завершена. Дані успішно ексфільтровані.")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    simulate_leak()