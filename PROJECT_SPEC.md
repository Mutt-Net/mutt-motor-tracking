# Project Specification

## Overview

**Project Name:** MuttLogbook (mutt-motor-tracking)

**Description:** A vehicle service logbook web application for tracking maintenance, modifications, costs, fuel economy, and VCDS fault codes. Originally built for a VW EOS but supports multiple vehicles.

**Version:** 1.3.0

**Repository:** https://github.com/Mutt-Net/mutt-motor-tracking

---

## Audience & Jobs to Be Done

### Primary Audience

**Who:** Car enthusiasts and vehicle owners who want detailed tracking of their vehicle's history, especially those with modified or performance vehicles.

**Context:** Users need to maintain comprehensive records of their vehicle for personal tracking, resale value documentation, or troubleshooting recurring issues.

### Jobs to Be Done

| JTBD ID | Statement | Desired Outcome |
|---------|-----------|-----------------|
| JTBD-001 | When performing vehicle maintenance, I want to log service records with full details, so I can track maintenance history and costs over time | Complete service history with cost tracking |
| JTBD-002 | When diagnosing vehicle issues, I want to import and track VCDS fault codes, so I can monitor recurring problems and verify repairs | Fault code history with status tracking |
| JTBD-003 | When planning modifications, I want to track planned, in-progress, and completed mods, so I can manage my build project effectively | Organized modification tracking with cost analysis |

---

## Topics of Concern (Activities)

### Activity: vehicle-management

**Related to:** JTBD-001

**Description:** Create, view, update, and delete vehicle profiles with detailed specifications

**Capability Depths:**
- **Basic:** Single vehicle with VIN, mileage, engine, transmission
- **Enhanced:** Multiple vehicles, photo management
- **Advanced:** Export/import vehicle data, CSV export

**Acceptance Criteria:**
- [ ] Can create vehicle with full specifications
- [ ] Can view vehicle dashboard with summary stats
- [ ] Can export vehicle data to JSON
- [ ] Cascade delete removes all related records

### Activity: service-tracking

**Related to:** JTBD-001

**Description:** Log maintenance records with cost, parts, labor, and shop information

**Capability Depths:**
- **Basic:** Date, category, description, cost
- **Enhanced:** Parts used, labor hours, shop name, notes
- **Advanced:** Service interval reminders, timeline calculations

**Acceptance Criteria:**
- [ ] Can create maintenance record with all fields
- [ ] Service timeline shows overdue/upcoming/ok status
- [ ] Maintenance costs aggregated in dashboard
- [ ] Records sorted by date descending

### Activity: modification-tracking

**Related to:** JTBD-003

**Description:** Track vehicle modifications through their lifecycle from planned to completed

**Capability Depths:**
- **Basic:** Description, status (planned/in-progress/completed)
- **Enhanced:** Parts list, cost tracking, installation date
- **Advanced:** Cost analysis by category, mod timeline

**Acceptance Criteria:**
- [ ] Can create mod with status workflow
- [ ] Mod costs included in total spend
- [ ] Can filter mods by status
- [ ] Parts stored as JSON array

### Activity: vcds-diagnostics

**Related to:** JTBD-002

**Description:** Import, parse, and track VCDS fault code scans

**Capability Depths:**
- **Basic:** Manual fault code entry
- **Enhanced:** Parse VCDS text format, import from file
- **Advanced:** Fault status tracking (active/cleared), detection/clear dates

**Acceptance Criteria:**
- [ ] Can paste VCDS scan text and auto-parse
- [ ] Can upload .txt/.csv file for import
- [ ] Faults display with address, code, description
- [ ] Can mark faults as cleared

### Activity: cost-analysis

**Related to:** JTBD-001, JTBD-003

**Description:** Track and analyze vehicle expenses across categories

**Capability Depths:**
- **Basic:** Amount, category, description
- **Enhanced:** Summary by category, date filtering
- **Advanced:** Dashboard charts, cost per mile calculations

**Acceptance Criteria:**
- [ ] Can log costs in categories (fuel, insurance, tax, etc.)
- [ ] Summary shows totals by category
- [ ] Dashboard displays spending charts
- [ ] Configurable what's included in "total spend"

---

## Technical Constraints

| Constraint | Description |
|------------|-------------|
| **Language** | Python 3.10+ |
| **Runtime** | Python 3.11+ (CI), SQLite 3 |
| **Database** | SQLite (database/logbook.db) |
| **Framework** | Flask 3.0.0, Flask-SQLAlchemy 3.1.1 |
| **Frontend** | Vanilla JavaScript, HTML5, CSS3, Chart.js |
| **External Services** | None (fully self-contained) |
| **Deployment** | Local server (python -m backend.app), Docker planned |

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Flask API      │────▶│   SQLite        │
│   (Vanilla JS)  │     │   (backend/)     │     │   Database      │
│   index.html    │     │   routes.py      │     │   logbook.db    │
│   app.js        │     │   models.py      │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   File Storage   │
                        │   uploads/       │
                        └──────────────────┘
```

### Key Components

| Component | Responsibility | Location |
|-----------|----------------|----------|
| Flask App | Application entry, static file serving | `backend/app.py` |
| Routes | REST API endpoints (~52 endpoints) | `backend/routes.py` |
| Models | SQLAlchemy ORM models (12 tables) | `backend/models.py` |
| Database | SQLite with SQLAlchemy | `database/logbook.db` |
| Frontend | Single-page app with views | `frontend/index.html`, `frontend/js/app.js` |
| Extensions | Flask-SQLAlchemy initialization | `backend/extensions.py` |

### Database Tables

- `vehicles` - Vehicle profiles
- `maintenance` - Service records
- `mods` - Modification tracking
- `costs` - Expense tracking
- `notes` - General notes
- `vcds_faults` - VCDS fault codes
- `fuel_entries` - Fuel log entries
- `reminders` - Service reminders
- `vehicle_photos` - Vehicle images
- `guides` - How-to guides/templates
- `settings` - Application settings
- `receipts` - Receipt documents
- `service_documents` - Service documentation

---

## Build & Test Commands

| Command | Purpose |
|---------|---------|
| `python -m backend.app` | Start the Flask server |
| `python -m pytest -v` | Run all tests verbosely |
| `python -m pytest --cov=backend --cov-report=term` | Run tests with coverage |
| `python -m pytest backend/tests/ --cov=backend --cov-fail-under=95` | CI test command |
| `python -m py_compile backend/app.py` | Syntax check (lint equivalent) |

---

## Existing Conventions

### Code Style

- **Python:** Standard library only (no Black/flake8 configured)
- **Syntax checking:** `python -m py_compile`
- **Imports:** Standard library imports first, then third-party, then local
- **Path handling:** Use `os.path.join()` for cross-platform compatibility

### Project Structure

```
mutt-motor-tracking/
├── backend/
│   ├── app.py              # Flask application entry
│   ├── routes.py           # API route handlers
│   ├── models.py           # SQLAlchemy models
│   ├── extensions.py       # Flask extensions init
│   ├── test_routes.py      # Legacy test file
│   └── tests/              # Test suite
│       ├── conftest.py     # Pytest fixtures
│       ├── factories.py    # Test data factories
│       ├── test_*.py       # Test modules
│       └── seed_data.py    # Test data seeding
├── frontend/
│   ├── index.html          # Main HTML application
│   ├── js/app.js           # Frontend JavaScript
│   └── css/style.css       # Styles
├── database/
│   └── logbook.db          # SQLite database (gitignored)
├── uploads/                # File uploads (gitignored)
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD configuration
└── Stratum - Qwen/         # Stratum agent configuration
```

### Naming Conventions

- **Files:** `snake_case.py` for Python, `kebab-case.html` for HTML
- **Functions:** `snake_case`
- **Classes:** `PascalCase` (SQLAlchemy models)
- **API Routes:** `kebab-case` in URLs, `snake_case` in JSON
- **Database Tables:** `snake_case` plural (e.g., `vehicles`, `maintenance`)

### API Conventions

- **Base URL:** `/api`
- **Response Format:** JSON
- **Success Responses:** `200 OK`, `201 Created` with JSON body
- **Error Responses:** `400 Bad Request`, `404 Not Found` with `{'error': 'message'}`
- **Date Format:** `YYYY-MM-DD` (ISO 8601 date only)
- **Timestamps:** UTC with timezone info

---

## Non-Goals

What this project explicitly does NOT do:

- Real-time vehicle telemetry or OBD-II live data
- Multi-user authentication or authorization
- Cloud synchronization or backup
- Mobile native applications (web-only)
- Integration with external automotive APIs

---

## Future Considerations

Nice-to-haves for later (not in current scope):

- Docker containerization (mentioned in README as "coming in v1.1.0")
- Receipt/document upload and storage
- Enhanced VCDS parsing with more format support
- Service interval notifications/alerts
- Multiple vehicle photo gallery
- Fuel economy tracking with MPG calculations

---

## Notes

- The project uses a **single SQLite database** file, making it portable
- **No frontend framework** - pure vanilla JavaScript for simplicity
- **CORS enabled** for potential future frontend/backend separation
- **Test coverage requirement:** 95% (enforced in CI)
- **Default vehicle:** VW EOS created on first run
- **Settings system:** Configurable currency, date format, mileage units, service intervals
