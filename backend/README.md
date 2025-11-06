# backend (eVidyaHub)

Quick helpers to run the project locally.

Requirements
- A Python 3.11+ virtual environment located at `backend/.venv` with dependencies installed.

Install dependencies (from project root `backend/`):

```powershell
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

Run both servers (Windows)

Option A — batch file (opens two windows):

```powershell
.\run_all.bat
```

Option B — PowerShell (starts processes):

```powershell
.\run_all.ps1
```

What these do
- Django dev server: http://127.0.0.1:8000
- Static server (serves `backend/static`): http://127.0.0.1:3000

Notes
- This project now defaults to using a local SQLite file for development (the file is `db.sqlite3` at the project root). The settings were changed so SQLite is used unless you explicitly opt-in to MySQL by setting the environment variable `USE_MYSQL=1`.
- `manage.py` is located in `backend/manage.py/manage.py` in this repo layout. The helper scripts already reference that path.

If you previously used a MySQL database and want to migrate the data to the local SQLite file, follow the steps below.

Data migration (MySQL -> SQLite) — recommended approach using Django
1. Configure settings to point to your MySQL DB temporarily (set `USE_MYSQL=1` and the appropriate `DB_*` env vars), then run:

```powershell
cd 'C:\Users\saman\Desktop\Project 2\backend'
& .\.venv\Scripts\python.exe .\manage.py makemigrations
& .\.venv\Scripts\python.exe .\manage.py migrate
& .\.venv\Scripts\python.exe .\manage.py dumpdata --exclude contenttypes --exclude auth.permission --natural-foreign --natural-primary > data.json
```

2. Switch back to SQLite (unset `USE_MYSQL` or set it to `0`), ensure migrations are applied, then load the data:

```powershell
$env:USE_MYSQL='0'
& .\.venv\Scripts\python.exe .\manage.py migrate
& .\.venv\Scripts\python.exe .\manage.py loaddata data.json
```

Notes and caveats
- The dump/load approach works well for most projects. If you have custom SQL, stored procedures, or DB-specific fields, manual adjustments may be necessary.
- Always keep a backup of your MySQL data before attempting a migration.
- If the dataset is large or you have binary fields, consider using a more robust migration path (export/import per-table or use a dedicated migration tool).

If you'd like, I can attempt to run the dump/load here if you provide MySQL access details or run the commands on your machine and I can guide you step-by-step.
