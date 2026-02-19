# MuttLogbook Entity Relationship Diagram

## ASCII Entity Maps

### 1. Core Database Schema

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                    VEHICLES                                          │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ PK  id                        INTEGER                                                │
│     name                      VARCHAR(100)  NOT NULL                               │
│     reg                       VARCHAR(20)   UNIQUE                                  │
│     vin                       VARCHAR(17)   UNIQUE                                  │
│     year                      INTEGER                                                │
│     make                      VARCHAR(50)                                           │
│     model                     VARCHAR(50)                                           │
│     engine                    VARCHAR(100)                                          │
│     transmission              VARCHAR(50)                                           │
│     mileage                  INTEGER                                                │
│     test_key                 VARCHAR(50)   INDEXED, NULLABLE                       │
│     created_at               DATETIME                                               │
└──────────────────────────────────────────────────────────────────────────────────────┘
         │
         │ 1:N Cascade Delete
         ▼
         
    ┌─────────────┬─────────────┬───────────────┬─────────────┬─────────────┬────────────┐
    ▼             ▼             ▼               ▼             ▼             ▼            ▼
┌────────┐  ┌────────┐  ┌───────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐
│MAINTEN │  │  MODS  │  │   COSTS   │  │  NOTES  │  │  GUIDES │  │  PHOTOS  │  │  FAULTS  │
│ANCE    │  │         │  │           │  │         │  │         │  │          │  │ (VCDS)   │
├────────┤  ├─────────┤  ├───────────┤  ├─────────┤  ├─────────┤  ├──────────┤  ├──────────┤
│PK id   │  │PK id    │  │PK id      │  │PK id    │  │PK id    │  │PK id     │  │PK id     │
│FK veh  │  │FK veh   │  │FK veh     │  │FK veh   │  │FK veh   │  │FK veh    │  │FK veh    │
│ date   │  │ date    │  │ date      │  │ date    │  │ title   │  │ filename │  │ address  │
│ mileage│  │ mileage │  │ amount    │  │ title   │  │ category│  │ caption  │  │ fault_  │
│ category│ │ category│  │ category  │  │ content │  │ content │  │ is_     │  │ code    │
│ desc   │  │ desc    │  │ desc      │  │ tags    │  │ is_     │  │ primary  │  │ status  │
│ cost   │  │ cost    │  │           │  │         │  │ template│  │          │  │ detected│
│ shop   │  │ parts   │  │           │  │         │  │         │  │          │  │ cleared │
│ notes  │  │ status  │  │           │  │         │  │         │  │          │  │         │
│ test_  │  │ notes  │  │ test_key  │  │ test_key│  │         │  │          │  │ test_   │
│ key    │  │ test_  │  │           │  │         │  │         │  │          │  │ key     │
│        │  │ key    │  │           │  │         │  │         │  │          │  │         │
└────────┘  └─────────┘  └───────────┘  └─────────┘  └─────────┘  └──────────┘  └──────────┘
    │             │             │               │             │              │              │
    └─────────────┴─────────────┴───────────────┴─────────────┴──────────────┴──────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
        ┌──────────┐            ┌──────────┐            ┌──────────┐
        │FUEL      │            │REMINDERS │            │ RECEIPTS │
        │ENTRIES  │            │          │            │          │
        ├─────────┤            ├──────────┤            ├──────────┤
        │PK id    │            │PK id     │            │PK id     │
        │FK veh   │            │FK veh    │            │FK veh    │
        │ date    │            │ type     │            │FK maint  │◄──┐
        │ mileage │            │interval_ │            │ date     │   │
        │ gallons │            │ miles    │            │ vendor   │   │
        │ price   │            │interval_ │            │ amount   │   │ 1:1
        │ total   │            │ months   │            │ category │   │ optional
        │ station │            │last_srvc│            │ notes    │   │ to
        │ notes   │            │next_due │            │ filename │   │
        │test_key │            │ notes   │            │test_key  │   │
        └─────────┘            │test_key │            └──────────┘   │
                              └──────────┘                           │
                                       │                             │
                                       │  ┌─────────────────────────┘
                                       │  │
                                       ▼  ▼
                                 ┌────────────────┐
                                 │SERVICE        │
                                 │DOCUMENTS      │
                                 ├───────────────┤
                                 │PK id          │
                                 │FK veh         │
                                 │FK maint       │
                                 │ title         │
                                 │ description   │
                                 │ document_type │
                                 │ filename     │
                                 │test_key      │
                                 └──────────────┘
```

---

## 2. API Endpoint Flow

```
                        ┌─────────────────────────────────────┐
                        │           CLIENT REQUEST              │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │         FLASK ROUTER                 │
                        │    (backend/routes.py)              │
                        └──────────────────┬──────────────────┘
                                           │
           ┌──────────────────────────────┼──────────────────────────────┐
           │                              │                              │
           ▼                              ▼                              ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   CRUD ROUTES       │  │  ANALYTICS ROUTES  │  │   UTILITY ROUTES   │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ /api/vehicles      │  │ /api/dashboard     │  │ /api/upload        │
│ /api/maintenance   │  │ /api/analytics     │  │ /api/settings      │
│ /api/mods         │  │ /api/maintenance/  │  │ /api/settings/     │
│ /api/costs        │  │        timeline    │  │        backup      │
│ /api/notes        │  │                    │  │ /api/settings/     │
│ /api/vcds         │  │                    │  │        export     │
│ /api/guides        │  │                    │  │                    │
│ /api/fuel         │  │                    │  │                    │
│ /api/reminders    │  │                    │  │                    │
│ /api/receipts     │  │                    │  │                    │
│ /api/documents    │  │                    │  │                    │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────────┐
                    │     SQLALCHEMY ORM           │
                    │     (backend/models.py)       │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       SQLITE DATABASE          │
                    └───────────────────────────────┘
```

---

## 3. Test Coverage Mapping

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           TEST COVERAGE MATRIX                                         │
├───────────────────────┬───────────────────────────────────────────────────────────────┤
│ MODULE                │ TEST FILE                  │ TESTS  │ STATUS                 │
├───────────────────────┼────────────────────────────┼────────┼───────────────────────┤
│ Vehicles              │ test_routes.py             │   8    │ ✅ PASSING            │
│ Maintenance           │ test_routes.py + timeline  │  13    │ ✅ PASSING            │
│ Mods                  │ test_routes.py             │   4    │ ✅ PASSING            │
│ Costs                 │ test_routes.py             │   3    │ ⚠️  MINOR ISSUES     │
│ Notes                 │ test_routes.py             │   3    │ ✅ PASSING            │
│ VCDS                  │ test_routes.py + import    │   5    │ ✅ PASSING            │
│ Guides                │ test_routes.py             │   6    │ ✅ PASSING            │
│ Photos                │ test_routes.py             │   3    │ ✅ PASSING            │
│ Fuel                  │ test_routes.py             │   4    │ ✅ PASSING            │
│ Reminders             │ test_routes.py             │   4    │ ✅ PASSING            │
│ Receipts              │ test_receipts.py          │  11    │ ✅ PASSING            │
│ Documents             │ test_documents.py         │   8    │ ✅ PASSING            │
│ Settings              │ test_settings.py          │  16    │ ✅ PASSING            │
│ Dashboard             │ test_routes.py             │   2    │ ✅ PASSING            │
│ Analytics             │ test_routes.py             │   3    │ ⚠️  MINOR ISSUES     │
│ Import/Export         │ test_import_export.py      │   8    │ ✅ PASSING            │
│ Integration           │ test_integration.py        │   9    │ ✅ PASSING            │
├───────────────────────┼────────────────────────────┼────────┼───────────────────────┤
│ TOTAL                 │                            │  119   │ ~78% PASSING          │
└───────────────────────┴────────────────────────────┴────────┴───────────────────────┘
```

---

## 4. Test Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         TEST DATA ISOLATION                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐        │
│   │                        TEST EXECUTION FLOW                              │        │
│   └─────────────────────────────────────────────────────────────────────────┘        │
│                                                                                     │
│         ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│         │   PYTEST     │         │   CONFTEST   │         │   FACTORY   │        │
│         │   DISCOVERY  │────────►│    FIXTURE   │────────►│   CREATION   │        │
│         └──────────────┘         └──────────────┘         └──────────────┘        │
│                                        │                         │                   │
│                                        ▼                         ▼                   │
│         ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│         │   TEST       │◄────────│    CREATE    │◄────────│    IN-MEM    │        │
│         │   EXECUTION │         │    TEST      │         │    SQLite    │        │
│         └──────────────┘         │    DATA      │         │    DATABASE  │        │
│                     │           └──────────────┘         └──────────────┘        │
│                     │                    │                                           │
│                     │                    ▼                                           │
│                     │           ┌──────────────┐                                    │
│                     │           │   API CALL   │                                    │
│                     │           │   (CLIENT)   │                                    │
│                     │           └──────────────┘                                    │
│                     │                    │                                           │
│                     └────────────────────┼─────────────────────────────────────────── │
│                                          ▼                                           │
│         ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│         │   ASSERTION   │         │   DATABASE   │         │    REPORT    │        │
│         │   CHECKS     │         │    RESET     │         │   GENERATE   │        │
│         └──────────────┘         └──────────────┘         └──────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         TEST MODE ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│   │   FRONTEND      │      │   BACKEND        │      │   DATABASE       │        │
│   │   SETTINGS UI   │─────►│   SETTINGS API  │─────►│   SETTINGS       │        │
│   └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│            │                         │                         │                   │
│            │                         │                         │                   │
│            ▼                         ▼                         ▼                   │
│   ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│   │ [✓] Test Mode   │      │ test_mode_      │      │ key: test_mode_ │        │
│   │ Test Key: xxx   │      │ enabled=true     │      │     enabled     │        │
│   │ [Include in     │      │ test_key=xxx     │      │ key: test_key   │        │
│   │  analytics]     │      │ include_test     │      │ key: include_   │        │
│   └──────────────────┘      │     data=false   │      │     test_data   │        │
│                            └──────────────────┘      └──────────────────┘        │
│                                        │                                           │
│                                        ▼                                           │
│                            ┌──────────────────────────────┐                        │
│                            │  ALL DATA MODELS:           │                        │
│                            │  test_key = VARCHAR(50)    │                        │
│                            │  INDEXED, NULLABLE         │                        │
│                            └──────────────────────────────┘                        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Service Timeline Status Logic

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    MAINTENANCE TIMELINE STATUS ALGORITHM                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   INPUT: vehicle_id, current_mileage                                                │
│                                                                                     │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │  FOR EACH service_type IN ['oil_change', 'brakes', 'tire_rotation', ...]│    │
│   │                                                                           │    │
│   │  1. GET last service record for this vehicle and service_type            │    │
│   │                                                                           │    │
│   │  2. CALCULATE next_due_date:                                             │    │
│   │       last_service_date + interval_months                                │    │
│   │                                                                           │    │
│   │  3. CALCULATE next_due_mileage:                                         │    │
│   │       last_service_mileage + interval_miles                             │    │
│   │                                                                           │    │
│   │  4. DETERMINE status:                                                   │    │
│   │                                                                           │    │
│   │       ┌──────────────────────────────────────────────────────────────┐   │    │
│   │       │                                                              │   │    │
│   │       │    IF next_due_date < today                                │   │    │
│   │       │       OR next_due_mileage < current_mileage                 │   │    │
│   │       │           THEN status = 'OVERDUE'                          │   │    │
│   │       │                                                              │   │    │
│   │       │    ELSE IF next_due_date <= today + 30 days               │   │    │
│   │       │           OR next_due_mileage <= current_mileage + 1000   │   │    │
│   │       │           THEN status = 'UPCOMING'                         │   │    │
│   │       │                                                              │   │    │
│   │       │    ELSE                                                      │   │    │
│   │       │           THEN status = 'OK'                                │   │    │
│   │       │                                                              │   │    │
│   │       └──────────────────────────────────────────────────────────────┘   │    │
│   │                                                                           │    │
│   │  5. CALCULATE days_until_due: next_due_date - today                     │    │
│   │     CALCULATE miles_until_due: next_due_mileage - current_mileage       │    │
│   │                                                                           │    │
│   │  6. APPEND to timeline array                                           │    │
│   │                                                                           │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│   OUTPUT: timeline[]                                                               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Integration Test Scenarios

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         E2E TEST SCENARIOS                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  SCENARIO 1: Complete Vehicle Lifecycle                                             │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │  POST /api/vehicles ──► CREATE vehicle                                    │     │
│  │  POST /api/maintenance ──► Add service record                              │     │
│  │  POST /api/mods ──► Add modification                                       │     │
│  │  GET /api/dashboard ──► Verify total_spent includes all                   │     │
│  │  DELETE /api/vehicles/{id} ──► Verify cascade delete                       │     │
│  └────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                     │
│  SCENARIO 2: Mod Status Progression                                                 │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │  POST /api/vehicles ──► CREATE vehicle                                    │     │
│  │  POST /api/mods ──► status='planned'                                      │     │
│  │  PUT /api/mods/{id} ──► status='in_progress'                              │     │
│  │  PUT /api/mods/{id} ──► status='completed'                                │     │
│  │  GET /api/dashboard ──► Verify mods_cost includes completed mods          │     │
│  └────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                     │
│  SCENARIO 3: Analytics with Date Filtering                                          │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │  POST /api/vehicles ──► CREATE vehicle                                    │     │
│  │  POST /api/maintenance ──► date=2024-01-01, cost=100                      │     │
│  │  POST /api/maintenance ──► date=2024-06-01, cost=100                      │     │
│  │  GET /api/analytics?start=2024-01-01&end=2024-03-31 ──► total=100        │     │
│  │  GET /api/analytics ──► total=200                                        │     │
│  └────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                     │
│  SCENARIO 4: Service Timeline with Overdue Status                                    │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │  POST /api/vehicles ──► mileage=50000                                    │     │
│  │  POST /api/maintenance ──► date=1 year ago, mileage=10000                │     │
│  │  GET /api/maintenance/timeline ──► oil_change status='overdue'           │     │
│  └────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. File Structure

```
mutt-logbook/
├── backend/
│   ├── __init__.py
│   ├── app.py                    # Flask application entry
│   ├── extensions.py             # SQLAlchemy initialization
│   ├── models.py                # All database models (13 models)
│   ├── routes.py                # All API routes (~64 endpoints)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py          # Pytest fixtures
│       ├── factories.py         # Data factories
│       ├── helpers.py           # Test utilities
│       ├── seed_data.py        # Database seeding
│       ├── test_routes.py      # Core endpoint tests
│       ├── test_receipts.py    # Receipt tests
│       ├── test_documents.py   # Document tests
│       ├── test_settings.py     # Settings tests
│       ├── test_timeline.py    # Timeline tests
│       ├── test_import_export.py # Import/export tests
│       └── test_integration.py  # E2E tests
│
├── .github/
│   └── workflows/
│       └── test.yml             # CI/CD workflow
│
├── docs/
│   ├── PLANNING.md              # Original planning doc
│   ├── QA_PROCESS.md            # This document
│   └── QA_ENTITY_MAP.md        # Entity relationship diagrams
│
└── frontend/
    ├── index.html
    ├── js/app.js
    └── css/style.css
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-19*
