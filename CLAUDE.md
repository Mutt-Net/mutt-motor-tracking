# Mutt Motor Tracking

Single-server Flask app: backend serves both API and static frontend.

## Commands

```bash
# Run the server (port 5000, serves frontend at /)
python -m backend.app

# Run all tests
python -m pytest backend/tests/ -v

# Run a specific test file
python -m pytest backend/tests/test_routes.py -v

# Run a single test by name
python -m pytest backend/tests/test_routes.py::TestVehicles::test_get_vehicles -v

# Run with coverage (CI requires ≥95%)
python -m pytest backend/tests/ --cov=backend --cov-report=term-missing -v

# Syntax check (no linter configured)
python -m py_compile backend/app.py backend/routes.py backend/models.py backend/extensions.py
```

## Architecture

- `backend/app.py` — app factory, DB init, static file routes (`/`, `/css/`, `/js/`). Creates default vehicle and settings on first run.
- `backend/routes.py` — all API endpoints as a single `routes` Blueprint, registered at `/api`. Also contains helpers: `parse_date`, `validate_required`, `calculate_maintenance_timeline`, `calculate_service_status`.
- `backend/models.py` — 13 SQLAlchemy models, all using `utc_now()` for timestamps.
- `backend/extensions.py` — single `db = SQLAlchemy()` instance (imported everywhere to avoid circular imports).
- `frontend/` — plain HTML/CSS/JS, no build step. `index.html` loads `js/app.js` and `css/style.css`.
- `database/logbook.db` — SQLite, auto-created on first run. Delete to reset.
- `uploads/` — receipts, documents, vehicle photos.
- `specs/` — feature specification markdown files.

## Models

13 models, all with `vehicle_id` FK and `cascade='all, delete-orphan'` (except `Guide`, which has `nullable=True` vehicle_id for global templates):

`Vehicle` → `Maintenance`, `Mod`, `Cost`, `Note`, `VCDSFault`, `Guide`, `VehiclePhoto`, `FuelEntry`, `Reminder`, `Receipt`, `ServiceDocument`

`Setting` — global key/value store (no vehicle FK). Keys: `currency_symbol`, `mileage_unit`, `date_format`, `service_intervals` (JSON), `total_spend_include_*` (booleans).

All models with user data have a `test_key` column (nullable, indexed) for test isolation.

## Conventions

**Route pattern:**
```python
@routes.get('/resource')
def get_resource():
    vehicle_id = request.args.get('vehicle_id')
    query = Model.query.filter_by(vehicle_id=vehicle_id)
    return jsonify([{...} for item in query.all()])
```

**Model pattern:** always include `vehicle_id` FK with `ondelete='CASCADE'`, `created_at` defaulting to `utc_now`. Use `test_key` for new models that need test isolation.

**File uploads:** `secure_filename_with_ext()` generates a UUID-based filename. `validate_filename()` is called before serving files.

**Service intervals:** defined as `SERVICE_INTERVALS` dict in `routes.py`; overridable via `Setting(key='service_intervals')`. `calculate_service_status()` returns `'overdue'`, `'upcoming'`, or `'ok'`.

## Tests

Tests live in `backend/tests/`. Conftest uses in-memory SQLite (`sqlite:///:memory:`) with function-scoped fixtures — each test gets a fresh DB.

Key fixtures in `conftest.py`: `app`, `client`, `db_session`, `test_vehicle`, `test_vehicle_2`, `sample_maintenance`, `sample_mod`, `sample_cost`, `sample_reminder`, `sample_fuel_entry`, `sample_receipt`, `sample_document`, `test_key`.

Helpers in `backend/tests/helpers.py`: `assert_response_success`, `assert_response_created`, `assert_response_not_found`, `create_test_vehicle`, `create_test_maintenance`, etc.

**Search `routes.py` and `models.py` before adding new endpoints or models.** The file is large — use Grep to find existing endpoints rather than reading the whole file.
