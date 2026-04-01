import psycopg2 # Треба буде встановити: pip install psycopg2-binary
import time

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
        
        print("🚀 Початок імітації витоку даних...")
        for i in range(10):
            cur.execute("SELECT * FROM users_private;")
            print(f"Запит {i+1} виконано")
            time.sleep(0.2) # Робимо запити кожні 200 мілісекунд (дуже швидко)
            
        cur.close()
        conn.close()
        print("✅ Імітація завершена.")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    simulate_leak()