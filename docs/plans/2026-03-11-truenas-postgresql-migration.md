# TrueNAS PostgreSQL Migration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the SQLite backend with PostgreSQL running in Docker on TrueNAS SCALE, with Flask containerised alongside it in a single Compose stack.

**Architecture:** Flask/Waitress + PostgreSQL in a `docker-compose.yml` deployed as a TrueNAS Custom App. Two ZFS datasets provide persistent storage: one for Postgres data files, one for uploaded files. The mobile app backend URL is updated in-app — no mobile code changes required.

**Tech Stack:** Python 3.12, Flask 3.0, SQLAlchemy, psycopg2-binary, PostgreSQL 16-alpine, Docker Compose, TrueNAS SCALE Custom Apps.

---

## Pre-flight Checklist

- Working directory for all commands: `Z:/Python/mutt-motor-tracking/`
- Docker must be installed on the dev machine for local build verification
- TrueNAS SCALE web UI accessible on LAN
- Git branch: work on `feature/truenas-postgresql` (create from current branch)

```bash
cd Z:/Python/mutt-motor-tracking
git checkout -b feature/truenas-postgresql
```

---

## Task 1: Add PostgreSQL Driver

SQLAlchemy needs `psycopg2` to talk to PostgreSQL. The binary wheel (`psycopg2-binary`) requires no system dependencies inside the Docker image.

**Files:**
- Modify: `requirements.txt`

**Step 1: Add the dependency**

Open `requirements.txt` and add after `waitress`:

```
psycopg2-binary>=2.9.9
```

Full file should read:
```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-cors>=4.0.0
pytest==8.0.0
pytest-flask==1.3.0
pytest-cov>=4.0.0
python-dateutil==2.8.2
waitress>=3.0.0
psycopg2-binary>=2.9.9
```

**Step 2: Verify the package resolves**

```bash
pip install psycopg2-binary
```

Expected: installs without error.

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore(deps): add psycopg2-binary for PostgreSQL support

-MuttNET-"
```

---

## Task 2: Update `backend/app.py` to Use `DATABASE_URL`

Replace the hardcoded SQLite path with an environment variable. This keeps credentials out of the repo and makes the same image work in any environment.

**Files:**
- Modify: `backend/app.py:13-14`

**Step 1: Open `backend/app.py` and find the URI line**

Current (line 13):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "logbook.db")}'
```

**Step 2: Replace with env var read**

```python
import os

_db_url = os.environ.get('DATABASE_URL')
if not _db_url:
    raise RuntimeError('DATABASE_URL environment variable is not set')
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
```

Place this immediately after `app = Flask(__name__)`. The `basedir` variable and the old URI line can be removed if nothing else references `basedir` — check with:

```bash
grep -n "basedir" backend/app.py
```

If `basedir` is only used for the SQLite path, delete it. If it's used for `frontend/` serving, keep it.

**Step 3: Verify the app still imports cleanly (without the env var set, it should raise clearly)**

```bash
python -c "import os; os.environ['DATABASE_URL']=''; from backend.app import app" 2>&1
```

Expected: `RuntimeError: DATABASE_URL environment variable is not set`

**Step 4: Commit**

```bash
git add backend/app.py
git commit -m "feat(config): read DATABASE_URL from environment variable

Removes hardcoded SQLite path. App raises clearly at startup if
DATABASE_URL is not set.

-MuttNET-"
```

---

## Task 3: Write the Dockerfile

Builds the Flask image from a slim Python base. The image is self-contained — code baked in, dependencies installed from `requirements.txt`.

**Files:**
- Create: `Dockerfile`

**Step 1: Create `Dockerfile` in the project root**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

Notes:
- `WORKDIR /app` means all relative paths in the app resolve from `/app`
- `COPY . .` copies the full project; `.dockerignore` (next step) excludes junk
- `CMD ["python", "backend/app.py"]` invokes waitress via the `if __name__ == '__main__'` block

**Step 2: Create `.dockerignore`**

```
__pycache__/
*.pyc
*.pyo
.git/
.gitignore
database/
instance/
backups/
*.md
docs/
specs/
*.txt.bak
```

This keeps the image lean — excludes SQLite database files, git history, and docs.

**Step 3: Build the image locally to verify**

```bash
DATABASE_URL=postgresql://logbook:test@localhost:5432/logbook docker build -t mutt-logbook-api .
```

Expected: build succeeds, no pip errors.

**Step 4: Commit**

```bash
git add Dockerfile .dockerignore
git commit -m "feat(docker): add Dockerfile and .dockerignore for Flask image

python:3.12-slim base, waitress entry point on port 5000.

-MuttNET-"
```

---

## Task 4: Write `docker-compose.yml`

Defines both services. The `db` service has a healthcheck so Flask waits for PostgreSQL to be fully ready before attempting `db.create_all()`.

**Files:**
- Create: `docker-compose.yml`

**Step 1: Create `docker-compose.yml` in the project root**

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: logbook
      POSTGRES_USER: logbook
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ${POSTGRES_DATA_PATH}:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logbook -d logbook"]
      interval: 5s
      timeout: 5s
      retries: 10

  api:
    build: .
    restart: unless-stopped
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://logbook:${POSTGRES_PASSWORD}@db:5432/logbook
    volumes:
      - ${UPLOADS_PATH}:/app/uploads
```

Variables (`POSTGRES_PASSWORD`, `POSTGRES_DATA_PATH`, `UPLOADS_PATH`) are injected via `.env` file or TrueNAS environment config — never hardcoded.

**Step 2: Create `.env` for local development**

```
POSTGRES_PASSWORD=localdevpassword
POSTGRES_DATA_PATH=./dev-postgres-data
UPLOADS_PATH=./uploads
```

Add `.env` to `.gitignore` so it is never committed:

```bash
echo ".env" >> .gitignore
echo "dev-postgres-data/" >> .gitignore
```

**Step 3: Verify Compose file is valid**

```bash
docker compose config
```

Expected: prints the resolved config with no errors.

**Step 4: Smoke test the full stack locally (requires Docker)**

```bash
docker compose up --build
```

Watch for:
- `db` reaching `healthy` state
- `api` container starting after db
- Flask log line: `Created default vehicle: VW EOS` (first-run seeding)
- `Serving on http://0.0.0.0:5000`

Then verify the API responds:

```bash
curl http://localhost:5000/api/vehicles
```

Expected: JSON array containing the default VW EOS vehicle.

Tear down:

```bash
docker compose down -v
```

**Step 5: Commit**

```bash
git add docker-compose.yml .gitignore
git commit -m "feat(docker): add docker-compose.yml for Flask + PostgreSQL stack

healthcheck on db ensures api waits for postgres ready state.
credentials injected via env vars, never hardcoded.

-MuttNET-"
```

---

## Task 5: TrueNAS Dataset Setup (Manual — One Time)

These steps are performed in the TrueNAS SCALE web UI before deploying.

**Step 1: Create the datasets**

In TrueNAS UI → **Datasets** → **Add Dataset** (twice):

| Dataset name | Suggested path |
|---|---|
| `logbook-postgres` | `/mnt/<pool>/logbook/postgres-data` |
| `logbook-uploads` | `/mnt/<pool>/logbook/uploads` |

Use default settings (no special compression or quota needed).

**Step 2: Note the full paths**

These are the values for `POSTGRES_DATA_PATH` and `UPLOADS_PATH` in the TrueNAS environment config.

**Step 3: Set permissions**

The PostgreSQL container runs as UID 999. Set dataset ownership:

In TrueNAS UI → **Datasets** → select `logbook-postgres` → **Edit Permissions** → set User to `999`, Group to `999`, apply recursively.

(The uploads dataset can stay as root — Flask runs as root inside the container.)

---

## Task 6: Deploy via Portainer

**Step 1: Push the branch to GitHub**

```bash
git push -u origin feature/truenas-postgresql
```

**Step 2: Open Portainer → Stacks → Add Stack**

In Portainer UI:
- **Stacks** → **Add stack**
- Name: `mutt-logbook`
- Select **Repository** tab (if pulling from Git) or **Web editor** (paste Compose file directly)

**If using Web editor:** paste the full contents of `docker-compose.yml`.

**If using Repository:** point at the repo URL and branch `feature/truenas-postgresql`, set Compose path to `docker-compose.yml`.

**Step 3: Set environment variables**

In the **Environment variables** section, add:

| Variable | Value |
|---|---|
| `POSTGRES_PASSWORD` | `<choose-a-strong-password>` |
| `POSTGRES_DATA_PATH` | `/mnt/<pool>/logbook/postgres-data` |
| `UPLOADS_PATH` | `/mnt/<pool>/logbook/uploads` |

**Step 4: Deploy the stack**

Click **Deploy the stack**. Portainer will pull the postgres image, build the Flask image, and start both containers.

**Step 5: Verify in Portainer**

In **Stacks** → `mutt-logbook` → **Logs** for the `api` container. Expected:
- `Created default vehicle: VW EOS`
- `Serving on http://0.0.0.0:5000`

**Step 6: Verify from the LAN**

From any device on the network:

```bash
curl http://<truenas-ip>:5000/api/vehicles
```

Expected: JSON array with VW EOS.

---

## Task 7: Update Mobile App Backend URL

No code change. In-app configuration only.

**Step 1: Open the mobile app → Settings screen**

**Step 2: Update the backend URL**

Change from: `http://<old-machine-ip>:5000`
Change to: `http://<truenas-ip>:5000`

**Step 3: Tap "Test Connection"**

Expected: green status indicator.

**Step 4: Trigger a manual sync**

Expected: sync completes without errors. All vehicle data appears in the app.

**Step 5: Verify a date-bearing record syncs correctly**

Create a maintenance entry with a date. Sync. Confirm it appears in:

```bash
curl http://<truenas-ip>:5000/api/vehicles/1/maintenance
```

Expected: record present with correct `YYYY-MM-DD` date format. PostgreSQL strict date handling means malformed dates will error here — this is the canary for any date format issues.

---

## Task 8: Merge and Clean Up

**Step 1: Open PR or merge directly**

```bash
git checkout main
git merge feature/truenas-postgresql
git push origin main
```

**Step 2: Remove the old SQLite database file from the repo (if tracked)**

```bash
git rm --cached database/logbook.db 2>/dev/null || true
echo "database/*.db" >> .gitignore
git add .gitignore
git commit -m "chore: remove SQLite db from tracking, add to gitignore

-MuttNET-"
```

**Step 3: Delete the old local SQLite backend process** (if it was running as a standalone Python process on a dev machine) — stop it and remove from startup.

---

## Verification Checklist

- [ ] `curl http://<truenas-ip>:5000/api/vehicles` returns vehicles JSON
- [ ] `curl http://<truenas-ip>:5000/api/vehicles/1/maintenance` returns maintenance records
- [ ] Mobile app connects and syncs without errors
- [ ] File upload (photo or document) saves and is retrievable
- [ ] TrueNAS restart → containers come back up automatically (`restart: unless-stopped`)
- [ ] `docker compose logs api` shows no ERROR lines after a clean sync
