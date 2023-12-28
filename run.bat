@echo off

if exist ".venv" (
    echo venv is exist
) else (
    python -m venv .venv
    call ".venv\scripts\activate"
    pip install -r requirements.txt
)
python main.py