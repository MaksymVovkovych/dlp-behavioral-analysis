@echo off
echo 🚀 Launching SentinelDB Portable for Windows...
REM Перевіряємо наявність віртуального середовища
if not exist .venv (
    echo ❌ Virtual environment not found! Please ensure .venv folder is on the drive.
    pause
    exit
)
REM Активація середовища (у Windows шлях саме такий)
call .venv\Scripts\activate
REM Запуск інтерфейсу
streamlit run app/gui.py
pause