@echo off
REM Run both backend (Django) and frontend (static files) in separate windows
SET ROOT_DIR=%~dp0
REM Use SQLite for quick local dev
start "Django Backend" powershell -NoExit -Command "cd '%ROOT_DIR%'; $env:USE_SQLITE='1'; $env:PYTHONPATH='%ROOT_DIR%'; .\.venv\Scripts\python.exe '.\manage.py\manage.py' runserver 8000"
start "Static Frontend" powershell -NoExit -Command "cd '%ROOT_DIR%static'; .\..\.venv\Scripts\python.exe -m http.server 3000"
echo Launched backend (http://127.0.0.1:8000) and static server (http://127.0.0.1:3000)
pause
