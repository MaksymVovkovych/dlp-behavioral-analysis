#!/bin/bash
echo "🚀 Запуск SentinelDB Portable..."
# Активуємо середовище прямо з папки проекту
source .venv/bin/activate
# Запускаємо інтерфейс
streamlit run app/gui.py