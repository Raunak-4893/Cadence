@echo off
REM ============================================================
REM  Cadence - Study Timetable   (one-click launcher for Windows)
REM  Put this file in the SAME folder as app.py and requirements.txt,
REM  then just double-click it.
REM ============================================================

setlocal
cd /d "%~dp0"

title Cadence - Study Timetable

REM --- 1. Find Python -----------------------------------------
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo.
    echo [ERROR] Python was not found on this PC.
    echo         Install it from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH" during setup.
    echo.
    pause
    exit /b 1
)

REM --- 2. Create the virtual environment (first run only) -----
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

REM --- 3. Install dependencies (first run, or if missing) -----
if not exist "venv\.installed" (
    echo Installing dependencies, please wait...
    "venv\Scripts\python.exe" -m pip install --upgrade pip
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed. Check your internet connection.
        pause
        exit /b 1
    )
    echo done> "venv\.installed"
)

REM --- 3b. Skip Streamlit's first-run "Email:" prompt ---------
REM  Without this, Streamlit pauses on a welcome prompt and the
REM  server never starts (browser shows "site can't be reached").
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    (
        echo [general]
        echo email = ""
    ) > "%USERPROFILE%\.streamlit\credentials.toml"
)

REM --- 4. Launch the app --------------------------------------
echo.
echo Starting Cadence... your browser will open shortly.
echo Keep this window open while using the app.
echo Close this window (or press Ctrl+C) to stop it.
echo.
"venv\Scripts\python.exe" -m streamlit run app.py

pause
endlocal
