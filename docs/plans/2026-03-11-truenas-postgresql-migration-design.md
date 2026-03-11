# TrueNAS PostgreSQL Migration — Design

Generated: 2026-03-11

## Summary

Migrate the mutt-motor-tracking backend from a SQLite file on a local machine to a
PostgreSQL container running on TrueNAS SCALE, alongside the Flask app in a Docker
Compose stack. The mobile app sync service is unaffected.

---

## Deployment Architecture

```
TrueNAS SCALE
└── Custom App: mutt-logbook
    ├── Container: api  (Flask/Waitress, port 5000)
    │   └── Build: Dockerfile in mutt-motor-tracking/
    └── Container: db   (postgres:16-alpine)

TrueNAS Datasets (bind-mounted):
├── /mnt/<pool>/logbook/postgres-data  → /var/lib/postgresql/data
└── /mnt/<pool>/logbook/uploads        → /app/uploads
```

- Open LAN access — no authentication required
- Mobile app backend URL updated in-app (Settings screen) to TrueNAS IP:5000
- No Nginx layer — Flask/Waitress serves both API and static frontend directly

---

## Repository Changes

Three files affected in `mutt-motor-tracking/`:

| File | Change |
|---|---|
| `Dockerfile` | New — builds Flask image from `python:3.12-slim` |
| `docker-compose.yml` | New — defines `db` (postgres:16-alpine) and `api` services |
| `backend/app.py` | Edit — read `DATABASE_URL` env var instead of hardcoded SQLite path |

Models, routes, and all business logic: untouched.

### Dockerfile (outline)
```
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "-m", "waitress", "--host=0.0.0.0", "--port=5000", "backend.app:app"]
```

### docker-compose.yml (outline)
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: logbook
      POSTGRES_USER: logbook
      POSTGRES_PASSWORD: <password>
    volumes:
      - /mnt/<pool>/logbook/postgres-data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://logbook:<password>@db:5432/logbook
    volumes:
      - /mnt/<pool>/logbook/uploads:/app/uploads
```

### app.py change
```python
# Replace hardcoded SQLite URI with:
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
```

---

## Data & File Persistence

| Dataset | Container mount | Contents |
|---|---|---|
| `logbook/postgres-data` | `/var/lib/postgresql/data` | PostgreSQL data files |
| `logbook/uploads` | `/app/uploads` | Photos, documents, receipts |

- Datasets created manually on TrueNAS before first deploy
- Fresh start — no SQLite data migration
- `db.create_all()` in `app.py` initialises all 12 tables on first run
- Default vehicle and settings seeding already guarded by existence checks
- ZFS snapshots cover both datasets automatically
- Logical DB backup: `docker exec mutt-logbook-db-1 pg_dump -U logbook logbook > backup.sql`

---

## Mobile App Changes

- **Backend URL:** Updated in-app via Settings screen to `http://<truenas-ip>:5000` — no code change
- **Sync service:** No changes — talks HTTP to Flask, DB is transparent
- **Date format:** Verify `sync.ts` sends ISO `YYYY-MM-DD` for all date fields — PostgreSQL is strict where SQLite was lenient

---

## Out of Scope

- Authentication (open LAN access is acceptable)
- Nginx reverse proxy (premature — Flask/Waitress sufficient for home LAN)
- Data migration from SQLite (fresh start agreed)
- External/internet access
