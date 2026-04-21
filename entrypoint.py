import streamlit.web.cli as stcli
import os, sys
from pathlib import Path

def resolve_path(path):
    basedir = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # Вказуємо шлях до нашого gui.py всередині пакету
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app/gui.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())