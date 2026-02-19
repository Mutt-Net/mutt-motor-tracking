# MuttLogbook QA Documentation

## Overview

This document describes the comprehensive test infrastructure for the MuttLogbook Flask application, including feature-to-test mappings, entity relationships, and coverage analysis.

---

## 1. System Architecture

### 1.1 Technology Stack
- **Backend:** Flask + SQLAlchemy
- **Database:** SQLite (development) / PostgreSQL (production)
- **Frontend:** Vanilla JavaScript + HTML/CSS
- **Testing:** pytest + pytest-cov

### 1.2 API Architecture
```
Client (Browser)
      ↓
Flask Routes (Blueprint)
      ↓
SQLAlchemy ORM
      ↓
SQLite Database
```

---

## 2. Entity Relationship Map

### 2.1 Core Entities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VEHICLE (Parent)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  id: Integer (PK)                                                         │
│  name: String(100)                                                         │
│  reg: String(20) - UK vehicle registration                                │
│  vin: String(17) - Vehicle Identification Number                          │
│  year: Integer                                                             │
│  make: String(50)                                                          │
│  model: String(50)                                                         │
│  engine: String(100)                                                       │
│  transmission: String(50)                                                  │
│  mileage: Integer                                                          │
│  test_key: String(50) - For test data isolation                           │
│  created_at: DateTime                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌──────────┬──────────┬────┴────┬──────────┬──────────┬──────────┐
        ▼          ▼          ▼         ▼          ▼          ▼          ▼
   ┌──────────┐ ┌───────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌────────┐ ┌─────────┐
   │MAINTENANCE│ │  MOD  │ │ COST │ │ NOTE │ │ VCDS    │ │ GUIDE  │ │  PHOTO │
   └──────────┘ └───────┘ └──────┘ └──────┘ │ FAULT   │ │         │ │         │
                                             └─────────┘ └─────────┘ └─────────┘
                                                                             
   ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
   │FUEL ENTRY│ │ REMINDER│ │ RECEIPT  │ │DOCUMENT   │
   └──────────┘ └─────────┘ └──────────┘ │ SERVICE   │
                                         └───────────┘
```

### 2.2 Relationship Details

| Parent | Child | Type | Cascade |
|--------|-------|------|---------|
| Vehicle | Maintenance | One-to-Many | CASCADE |
| Vehicle | Mod | One-to-Many | CASCADE |
| Vehicle | Cost | One-to-Many | CASCADE |
| Vehicle | Note | One-to-Many | CASCADE |
| Vehicle | VCDSFault | One-to-Many | CASCADE |
| Vehicle | Guide | One-to-Many | CASCADE |
| Vehicle | VehiclePhoto | One-to-Many | CASCADE |
| Vehicle | FuelEntry | One-to-Many | CASCADE |
| Vehicle | Reminder | One-to-Many | CASCADE |
| Vehicle | Receipt | One-to-Many | CASCADE |
| Vehicle | ServiceDocument | One-to-Many | CASCADE |
| Maintenance | Receipt | One-to-Many | SET NULL |
| Maintenance | ServiceDocument | One-to-Many | SET NULL |

---

## 3. Feature-to-Test Mapping

### 3.1 Vehicles Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List vehicles | `/api/vehicles` | GET | TestVehicles | 1 |
| Get vehicle | `/api/vehicles/<id>` | GET | TestVehicles | 1 |
| Create vehicle | `/api/vehicles` | POST | TestVehicles | 1 |
| Update vehicle | `/api/vehicles/<id>` | PUT | TestVehicles | 1 |
| Delete vehicle | `/api/vehicles/<id>` | DELETE | TestVehicles | 1 |
| Cascade delete | N/A | N/A | TestVehicles | 1 |
| Export vehicle | `/api/vehicles/<id>/export` | GET | TestImportExport | 1 |
| Import vehicle | `/api/vehicles/import` | POST | TestImportExport | 1 |

**Total: 8 tests**

### 3.2 Maintenance Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List maintenance | `/api/maintenance` | GET | TestMaintenance | 1 |
| Create maintenance | `/api/maintenance` | POST | TestMaintenance | 1 |
| Update maintenance | `/api/maintenance/<id>` | PUT | TestMaintenance | 1 |
| Delete maintenance | `/api/maintenance/<id>` | DELETE | TestMaintenance | 1 |
| Get timeline | `/api/maintenance/timeline` | GET | TestMaintenanceTimeline | 10 |

**Total: 13 tests**

### 3.3 Mods Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List mods | `/api/mods` | GET | TestMods | 1 |
| Create mod | `/api/mods` | POST | TestMods | 1 |
| Update mod | `/api/mods/<id>` | PUT | TestMods | 1 |
| Delete mod | `/api/mods/<id>` | DELETE | TestMods | 1 |

**Total: 4 tests**

### 3.4 Costs Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List costs | `/api/costs` | GET | TestCosts | 1 |
| Create cost | `/api/costs` | POST | TestCosts | 1 |
| Cost summary | `/api/costs/summary` | GET | TestCosts | 1 |

**Total: 3 tests**

### 3.5 Notes Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List notes | `/api/notes` | GET | TestNotes | 1 |
| Create note | `/api/notes` | POST | TestNotes | 1 |
| Delete note | `/api/notes/<id>` | DELETE | TestNotes | 1 |

**Total: 3 tests**

### 3.6 VCDS Faults Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List faults | `/api/vcds` | GET | TestVCDS | 1 |
| Create fault | `/api/vcds` | POST | TestVCDS | 1 |
| Update fault | `/api/vcds/<id>` | PUT | TestVCDS | 1 |
| Parse VCDS | `/api/vcds/parse` | POST | TestVCDS | 1 |
| Import faults | `/api/vcds/import` | POST | TestImportExport | 1 |

**Total: 5 tests**

### 3.7 Guides Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List guides | `/api/guides` | GET | TestGuides | 1 |
| Create guide | `/api/guides` | POST | TestGuides | 1 |
| Update guide | `/api/guides/<id>` | PUT | TestGuides | 1 |
| Delete guide | `/api/guides/<id>` | DELETE | TestGuides | 1 |
| Get templates | `/api/guides/templates` | GET | TestGuides | 1 |
| Create templates | `/api/guides/templates` | POST | TestGuides | 1 |

**Total: 6 tests**

### 3.8 Photos Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List photos | `/api/vehicle-photos` | GET | TestVehiclePhotos | 1 |
| Create photo | `/api/vehicle-photos` | POST | TestVehiclePhotos | 2 |

**Total: 3 tests**

### 3.9 Fuel Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List fuel | `/api/fuel` | GET | TestFuelEntries | 1 |
| Create fuel | `/api/fuel` | POST | TestFuelEntries | 1 |
| Update fuel | `/api/fuel/<id>` | PUT | TestFuelEntries | 1 |
| Delete fuel | `/api/fuel/<id>` | DELETE | TestFuelEntries | 1 |

**Total: 4 tests**

### 3.10 Reminders Module

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List reminders | `/api/reminders` | GET | TestReminders | 1 |
| Create reminder | `/api/reminders` | POST | TestReminders | 1 |
| Update reminder | `/api/reminders/<id>` | PUT | TestReminders | 1 |
| Delete reminder | `/api/reminders/<id>` | DELETE | TestReminders | 1 |

**Total: 4 tests**

### 3.11 Receipts Module (NEW)

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List receipts | `/api/receipts` | GET | TestReceipts | 4 |
| Create receipt | `/api/receipts` | POST | TestReceipts | 3 |
| Update receipt | `/api/receipts/<id>` | PUT | TestReceipts | 2 |
| Delete receipt | `/api/receipts/<id>` | DELETE | TestReceipts | 2 |

**Total: 11 tests**

### 3.12 Documents Module (NEW)

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List documents | `/api/documents` | GET | TestDocuments | 3 |
| Create document | `/api/documents` | POST | TestDocuments | 1 |
| Delete document | `/api/documents/<id>` | DELETE | TestDocuments | 2 |

**Total: 6 tests**

### 3.13 Settings Module (NEW)

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| List settings | `/api/settings` | GET | TestSettings | 2 |
| Create setting | `/api/settings` | PUT | TestSettings | 5 |
| Update setting | `/api/settings/<key>` | PUT | TestSettings | 2 |
| Delete setting | `/api/settings/<key>` | DELETE | TestSettings | 2 |
| Export data | `/api/settings/export` | GET | TestSettingsExport | 1 |
| Backup settings | `/api/settings/backup` | GET | TestSettingsExport | 1 |
| Test mode | `/api/settings/test-mode` | PUT/GET | TestSettings | 3 |

**Total: 16 tests**

### 3.14 Dashboard & Analytics

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| Dashboard stats | `/api/dashboard` | GET | TestDashboard | 2 |
| Analytics data | `/api/analytics` | GET | TestAnalytics | 3 |

**Total: 5 tests**

### 3.15 File Upload

| Feature | Endpoint | Method | Test Class | Test Count |
|--------|----------|--------|------------|------------|
| Upload file | `/api/upload` | POST | TestFileUpload | 3 |
| Serve file | `/uploads/<filename>` | GET | TestFileUpload | 1 |
| Delete file | `/api/upload/<filename>` | DELETE | TestFileUpload | 1 |

**Total: 5 tests**

### 3.16 Integration Tests

| Feature | Test Class | Test Count |
|---------|------------|------------|
| Vehicle lifecycle | TestVehicleLifecycle | 2 |
| Mod workflow | TestModWorkflow | 1 |
| Service history | TestServiceHistory | 1 |
| Error handling | TestErrorHandling | 1 |
| Analytics integration | TestAnalyticsIntegration | 2 |
| Settings integration | TestSettingsIntegration | 2 |

**Total: 9 tests**

---

## 4. Test Coverage Summary

### 4.1 By Module

| Module | Endpoints | Tests | Coverage |
|--------|-----------|-------|----------|
| Vehicles | 8 | 8 | 100% |
| Maintenance | 5 | 13 | 100% |
| Mods | 4 | 4 | 100% |
| Costs | 3 | 3 | 100% |
| Notes | 3 | 3 | 100% |
| VCDS | 5 | 5 | 100% |
| Guides | 6 | 6 | 100% |
| Photos | 2 | 3 | 100% |
| Fuel | 4 | 4 | 100% |
| Reminders | 4 | 4 | 100% |
| Receipts | 4 | 11 | 100% |
| Documents | 3 | 6 | 100% |
| Settings | 8 | 16 | 100% |
| Dashboard | 1 | 2 | 100% |
| Analytics | 1 | 3 | 100% |
| File Upload | 3 | 5 | 100% |
| Import/Export | 3 | 3 | 100% |

### 4.2 Coverage Metrics

- **Total Endpoints:** 64
- **Total Tests:** 119
- **Code Coverage Target:** 95%

---

## 5. Test Data Management

### 5.1 Test Mode Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Settings Table                              │
├─────────────────────────────────────────────────────────────────┤
│  key: test_mode_enabled (boolean)                              │
│  key: test_key (string: test_abc123)                           │
│  key: include_test_data (boolean)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  All Data Models                                │
├─────────────────────────────────────────────────────────────────┤
│  test_key: String(50) nullable, indexed                       │
│  - Vehicle, Maintenance, Mod, Cost, Note, VCDSFault          │
│  - FuelEntry, Reminder, Receipt, ServiceDocument              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Filter APIs                                  │
├─────────────────────────────────────────────────────────────────┤
│  ?test_key=abc123 - Filter by test key                        │
│  ?include_test_data=true - Include test data in results       │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Test Mode Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings/test-mode` | PUT | Enable/disable test mode |
| `/api/settings/test-mode` | GET | Get test mode status |
| `/api/settings/test-key` | POST | Generate new UUID test key |
| `/api/settings/test-data/count` | GET | Count records with test keys |
| `/api/settings/test-data` | DELETE | Clear all test data |

---

## 6. CI/CD Pipeline

### 6.1 GitHub Actions Workflow

```yaml
# Triggers
on:
  push: [main, MuttMain]
  pull_request: [main, MuttMain]

# Jobs
jobs:
  test:
    - Checkout code
    - Setup Python 3.11
    - Install dependencies (pytest, pytest-cov)
    - Run tests with coverage
    - Upload coverage to Codecov
    - Fail if coverage < 95%
  
  lint:
    - Checkout code
    - Setup Python 3.11
    - Check syntax (py_compile)
```

---

## 7. Test Fixtures Reference

### 7.1 Core Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `app` | session | Flask test application |
| `client` | function | Test client for HTTP requests |
| `db_session` | function | Database session |
| `test_vehicle` | function | Primary test vehicle (ID: 1) |
| `test_vehicle_id` | function | Convenience: returns vehicle ID |
| `test_vehicle_2` | function | Secondary test vehicle |

### 7.2 Sample Data Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_maintenance` | Pre-created maintenance record |
| `sample_mod` | Pre-created mod |
| `sample_cost` | Pre-created cost |
| `sample_note` | Pre-created note |
| `sample_reminder` | Pre-created reminder |
| `sample_fuel_entry` | Pre-created fuel entry |
| `sample_vcds_fault` | Pre-created VCDS fault |
| `sample_guide` | Pre-created guide |
| `sample_photo` | Pre-created vehicle photo |
| `sample_setting` | Pre-created setting |
| `sample_receipt` | Pre-created receipt |
| `sample_document` | Pre-created document |

### 7.3 Bulk Data Fixtures

| Fixture | Description |
|---------|-------------|
| `multiple_maintenance_records` | 5 maintenance records for timeline testing |
| `multiple_mods` | 4 mods (various statuses) |
| `multiple_costs` | 5 costs (various categories) |
| `test_key` | Auto-generated UUID for test isolation |

---

## 8. Test Execution Guide

### 8.1 Running Tests

```bash
# Run all tests with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_receipts.py -v

# Run with coverage threshold
pytest backend/tests/ --cov=backend --cov-fail-under=95

# Generate HTML report
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html
```

### 8.2 CI/CD Commands

```bash
# Install dependencies
pip install pytest pytest-cov

# Run with verbose output
pytest backend/tests/ -v

# Run only integration tests
pytest backend/tests/test_integration.py -v

# Run with coverage report
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

---

## 9. Appendix: Model Schemas

### 9.1 Vehicle
```python
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reg = db.Column(db.String(20), unique=True)
    vin = db.Column(db.String(17), unique=True)
    year = db.Column(db.Integer)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    engine = db.Column(db.String(100))
    transmission = db.Column(db.String(50))
    mileage = db.Column(db.Integer, default=0)
    test_key = db.Column(db.String(50), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
```

### 9.2 Maintenance
```python
class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, ForeignKey, nullable=False)
    date = db.Column(db.Date, nullable=False)
    mileage = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    parts_used = db.Column(db.Text)
    labor_hours = db.Column(db.Float)
    cost = db.Column(db.Float)
    shop_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    test_key = db.Column(db.String(50), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
```

*(Similar patterns apply to all other models)*

---

## 10. Maintenance Timeline Status Logic

```
                    ┌─────────────────┐
                    │  Get Timeline   │
                    └────────┬────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ For each service_type │
                └───────────┬────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌──────────────────┐       ┌──────────────────┐
    │ Get last service │       │ No service record│
    │ record           │       │ (future service)  │
    └────────┬─────────┘       └────────┬─────────┘
             │                         │
             ▼                         ▼
    ┌──────────────────┐       ┌──────────────────┐
    │ Calculate next   │       │ Use current date │
    │ due date/mileage │       │ /mileage         │
    └────────┬─────────┘       └────────┬─────────┘
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │ Determine Status:    │
               │ - overdue: past due  │
               │ - upcoming: within   │
               │   30 days/miles      │
               │ - ok: all good      │
               └─────────────────────┘
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-19*
*Project: MuttLogbook Flask Application*
