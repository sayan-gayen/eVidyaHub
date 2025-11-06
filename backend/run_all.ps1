# Run both Django backend and a simple static file server for frontend
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

Write-Host "Starting Django backend on http://127.0.0.1:8000 (uses SQLite for dev)..."
Start-Process -FilePath "$venvPython" -ArgumentList "'.\\manage.py\\manage.py' runserver 8000" -NoNewWindow

Start-Sleep -Milliseconds 500
Write-Host "Starting static server on http://127.0.0.1:3000 (serving ./static)..."
Start-Process -FilePath "$venvPython" -ArgumentList "-m http.server 3000" -WorkingDirectory (Join-Path $projectRoot 'static') -NoNewWindow

Write-Host "Both servers started. Open http://127.0.0.1:8000 and http://127.0.0.1:3000"
