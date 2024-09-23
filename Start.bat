@echo off

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Activating virtual environment...
    call venv\Scripts\activate
    echo Installing dependencies from requirements.txt...
    pip install -r src/requirements.txt
) ELSE (
    echo Activating existing virtual environment...
    call venv\Scripts\activate
)

cls

echo Starting the application...
python src/main.py

cmd /k
