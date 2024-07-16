@echo off
IF NOT EXIST "venv\Scripts\activate.bat" (
    python -m venv venv
)

call venv\Scripts\activate

pip install -r src/requirements.txt

cls

python src/main.py

cmd /k
