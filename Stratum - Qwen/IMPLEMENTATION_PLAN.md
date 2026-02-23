# Implementation Plan

## Status
- **Total tasks:** 43
- **Completed:** 3
- **Remaining:** 40
- **Generated:** 2026-02-23
- **Last Updated:** 2026-02-23

---

## Discovery Summary

### Current State Analysis (Updated 2026-02-23)

**CRITICAL FINDING:** The actual application code does NOT exist in this directory.

**What exists:**
- Stratum framework files (loop.ps1, prompts, etc.)
- Documentation (API_REFERENCE.md, specs/)
- PROJECT_SPEC.md (filled in)
- AGENTS.md (configured for Python/Flask)
- This IMPLEMENTATION_PLAN.md

**What does NOT exist:**
- No `backend/` directory
- No `frontend/` directory  
- No application code whatsoever

**Reality Check:**
This is a greenfield project. The application needs to be built from scratch based on the specifications.

### Revised Approach

This project requires **greenfield development** of:
1. Flask backend with SQLAlchemy models (12 models)
2. Vanilla JS frontend (SPA with 9 views)
3. pytest test suite (95% coverage target)
4. All specification documents (5 created)

---

## Tasks

### Phase 1: Foundation

- [x] **TASK-001**: Create PROJECT_SPEC.md with JTBD and activities
  - Spec: N/A (greenfield project)
  - Required tests: N/A (documentation task)
  - Notes: Created comprehensive PROJECT_SPEC.md with 7 activities: vehicle-management, service-tracking, modification-tracking, vcds-diagnostics, cost-analysis, fuel-tracking, documentation. Completed: 2026-02-23

- [x] **TASK-002**: Create specs directory with capability depth specifications
  - Spec: `PROJECT_SPEC.md` - Topics of Concern
  - Required tests: N/A (documentation task)
  - Notes: Created 5 specification files in specs/ directory:
    - specs/vehicle-management.md
    - specs/service-tracking.md
    - specs/modification-tracking.md
    - specs/vcds-diagnostics.md
    - specs/cost-analysis.md
  - Completed: 2026-02-23

- [x] **TASK-003**: Update AGENTS.md with Python/Flask build commands
  - Spec: N/A (operational configuration)
  - Required tests: N/A (configuration task)
  - Notes: Updated with pytest, black, isort commands. Added project structure. Completed: 2026-02-23

- [ ] **TASK-004**: Create backend directory structure
  - Spec: `AGENTS.md` - Project Structure
  - Required tests: N/A (infrastructure task)
  - Notes: Create backend/, backend/tests/, frontend/, uploads/ directories

- [ ] **TASK-005**: Create Flask application entry point
  - Spec: `AGENTS.md` - Project Structure
  - Required tests: Test that app starts and health endpoint works
  - Notes: Create backend/app.py with basic Flask app and health check

- [ ] **TASK-006**: Create SQLAlchemy database configuration
  - Spec: `PROJECT_SPEC.md` - Technical Constraints
  - Required tests: Test database connection and table creation
  - Notes: Configure SQLite with SQLAlchemy, create models.py base

### Phase 2: Data Models

- [ ] **TASK-010**: Create Vehicle model
  - Spec: `specs/vehicle-management.md` - Core Vehicle Entity
  - Required tests: Create, read, update vehicle; validate required fields
  - Notes: Fields: id, name, make, model, year, vin, license_plate, color, mileage, purchase_date, purchase_price, is_active

- [ ] **TASK-011**: Create VehiclePhoto model
  - Spec: `specs/vehicle-management.md` - Photo Management
  - Required tests: Photo CRUD, primary photo flag behavior
  - Notes: Relationship to Vehicle with cascade delete

- [ ] **TASK-012**: Create Service model
  - Spec: `specs/service-tracking.md` - Core Service Entity
  - Required tests: Service CRUD, parts_used JSON handling
  - Notes: Fields include parts_used as JSON text

- [ ] **TASK-013**: Create ServiceInterval and Reminder models
  - Spec: `specs/service-tracking.md` - Service Intervals
  - Required tests: Interval CRUD, reminder generation
  - Notes: Auto-update intervals when service logged

- [ ] **TASK-014**: Create Modification model
  - Spec: `specs/modification-tracking.md` - Core Modification Entity
  - Required tests: Mod CRUD, status workflow, parts JSON
  - Notes: Status: planned/in_progress/completed

- [ ] **TASK-015**: Create FaultCode model
  - Spec: `specs/vcds-diagnostics.md` - Fault Code Entity
  - Required tests: Fault CRUD, status tracking, clear date
  - Notes: Status: active/cleared

- [ ] **TASK-016**: Create Cost model
  - Spec: `specs/cost-analysis.md` - Core Cost Entity
  - Required tests: Cost CRUD, category filtering, date filtering
  - Notes: Standard categories for filtering

- [ ] **TASK-017**: Create FuelEntry model
  - Spec: `PROJECT_SPEC.md` - Fuel Tracking
  - Required tests: Fuel entry CRUD, MPG calculation
  - Notes: Fields: date, mileage, gallons, price_per_gallon, station

- [ ] **TASK-018**: Create Document and Note models
  - Spec: `PROJECT_SPEC.md` - Documentation
  - Required tests: Document/note CRUD, file upload handling
  - Notes: Document has file upload, Note is text only

- [ ] **TASK-019**: Create Settings and Guide models
  - Spec: `PROJECT_SPEC.md` - Settings system
  - Required tests: Settings CRUD, guide template loading
  - Notes: Settings as key-value pairs

### Phase 3: API Endpoints - Vehicles

- [ ] **TASK-020**: Implement vehicle CRUD endpoints
  - Spec: `specs/vehicle-management.md` - CRUD Operations
  - Required tests: POST/GET/PUT/DELETE vehicles, validation
  - Notes: /api/vehicles routes

- [ ] **TASK-021**: Implement vehicle photo upload endpoints
  - Spec: `specs/vehicle-management.md` - Photo Management
  - Required tests: Upload, retrieve, delete, set primary
  - Notes: Multipart/form-data, file validation

- [ ] **TASK-022**: Implement vehicle import/export endpoints
  - Spec: `specs/vehicle-management.md` - Import/Export
  - Required tests: Export JSON, import JSON, CSV export
  - Notes: Preserve relationships on import

### Phase 4: API Endpoints - Service

- [ ] **TASK-030**: Implement service CRUD endpoints
  - Spec: `specs/service-tracking.md` - CRUD Operations
  - Required tests: Service CRUD, vehicle filter
  - Notes: /api/maintenance routes

- [ ] **TASK-031**: Implement service interval endpoints
  - Spec: `specs/service-tracking.md` - Service Intervals
  - Required tests: Interval CRUD, auto-update on service
  - Notes: /api/maintenance/intervals

- [ ] **TASK-032**: Implement reminder endpoints
  - Spec: `specs/service-tracking.md` - Automatic Reminder Creation
  - Required tests: Get reminders, complete reminder, status filter
  - Notes: /api/maintenance/reminders

- [ ] **TASK-033**: Implement timeline endpoint
  - Spec: `specs/service-tracking.md` - Maintenance Timeline
  - Required tests: Timeline calculation, status (ok/upcoming/overdue)
  - Notes: /api/maintenance/timeline

### Phase 5: API Endpoints - Modifications

- [ ] **TASK-040**: Implement modification CRUD endpoints
  - Spec: `specs/modification-tracking.md` - CRUD Operations
  - Required tests: Mod CRUD, vehicle/status filters
  - Notes: /api/mods routes

- [ ] **TASK-041**: Implement mod status workflow endpoint
  - Spec: `specs/modification-tracking.md` - Status Workflow
  - Required tests: Update status, validate transitions
  - Notes: /api/mods/<id>/status

- [ ] **TASK-042**: Implement mod summary endpoint
  - Spec: `specs/modification-tracking.md` - Cost Aggregation
  - Required tests: Aggregation by status, dashboard integration
  - Notes: Include in /api/dashboard

### Phase 6: API Endpoints - VCDS

- [ ] **TASK-050**: Implement fault code CRUD endpoints
  - Spec: `specs/vcds-diagnostics.md` - CRUD Operations
  - Required tests: Fault CRUD, vehicle/status filters
  - Notes: /api/vcds routes

- [ ] **TASK-051**: Implement VCDS parser endpoint
  - Spec: `specs/vcds-diagnostics.md` - VCDS Text Parsing
  - Required tests: Parse various VCDS formats
  - Notes: /api/vcds/parse

- [ ] **TASK-052**: Implement fault import endpoint
  - Spec: `specs/vcds-diagnostics.md` - Import Parsed Codes
  - Required tests: Import parsed faults, skip_existing option
  - Notes: /api/vcds/import

- [ ] **TASK-053**: Implement fault clear/activate endpoints
  - Spec: `specs/vcds-diagnostics.md` - Fault Status Tracking
  - Required tests: Clear fault, reactivate fault, track dates
  - Notes: /api/vcds/<id>/clear, /api/vcds/<id>/activate

### Phase 7: API Endpoints - Costs

- [ ] **TASK-060**: Implement cost CRUD endpoints
  - Spec: `specs/cost-analysis.md` - CRUD Operations
  - Required tests: Cost CRUD, vehicle/category filters
  - Notes: /api/costs routes

- [ ] **TASK-061**: Implement cost summary endpoint
  - Spec: `specs/cost-analysis.md` - Cost Summary
  - Required tests: Summary with date/category filters, by_category
  - Notes: /api/costs/summary

- [ ] **TASK-062**: Implement analytics spending endpoint
  - Spec: `specs/cost-analysis.md` - Dashboard Spending Charts
  - Required tests: Chart data by category and month
  - Notes: /api/analytics/spending

### Phase 8: Dashboard & Analytics

- [ ] **TASK-070**: Implement dashboard endpoint
  - Spec: All specs - Dashboard integration
  - Required tests: Dashboard returns all aggregated stats
  - Notes: /api/dashboard - vehicles, services, mods, costs, faults

- [ ] **TASK-071**: Implement settings endpoints
  - Spec: `PROJECT_SPEC.md` - Settings system
  - Required tests: Get/update settings, total spend categories
  - Notes: /api/settings

### Phase 9: Frontend Foundation

- [ ] **TASK-080**: Create frontend HTML structure
  - Spec: `PROJECT_SPEC.md` - Architecture
  - Required tests: N/A (frontend task)
  - Notes: Single-page app with 9 views

- [ ] **TASK-081**: Implement vehicle management UI
  - Spec: `specs/vehicle-management.md` - Acceptance Criteria
  - Required tests: Manual testing, UI interactions work
  - Notes: Vehicle list, add/edit form, photo upload

- [ ] **TASK-082**: Implement service tracking UI
  - Spec: `specs/service-tracking.md` - Acceptance Criteria
  - Required tests: Manual testing, timeline displays
  - Notes: Service list, timeline view, add/edit form

- [ ] **TASK-083**: Implement modification tracking UI
  - Spec: `specs/modification-tracking.md` - Acceptance Criteria
  - Required tests: Manual testing, status workflow
  - Notes: Mod list, status workflow, cost display

- [ ] **TASK-084**: Implement VCDS diagnostics UI
  - Spec: `specs/vcds-diagnostics.md` - Acceptance Criteria
  - Required tests: Manual testing, parse/import works
  - Notes: Fault list, paste/import, manual entry

- [ ] **TASK-085**: Implement cost analysis UI
  - Spec: `specs/cost-analysis.md` - Acceptance Criteria
  - Required tests: Manual testing, charts display
  - Notes: Cost list, summary, Chart.js integration

### Phase 10: Testing & Quality

- [ ] **TASK-090**: Create pytest fixtures and factories
  - Spec: `AGENTS.md` - Testing Patterns
  - Required tests: Fixtures work, factories create valid data
  - Notes: conftest.py, factories.py

- [ ] **TASK-091**: Add model tests for all entities
  - Spec: All model specs
  - Required tests: Test all 12 models, relationships, cascade delete
  - Notes: test_models.py

- [ ] **TASK-092**: Add route tests for all endpoints
  - Spec: All API specs
  - Required tests: Test all endpoints, validation, error handling
  - Notes: test_routes.py

- [ ] **TASK-093**: Verify 95% test coverage
  - Spec: `PROJECT_SPEC.md` - Build & Test Commands
  - Required tests: pytest --cov=backend --cov-fail-under=95
  - Notes: Run coverage, add missing tests

---

## Prioritization Rationale

1. **Phase 1 (Foundation)**: Create directory structure, Flask app, database config
2. **Phase 2 (Models)**: Implement all 12 SQLAlchemy models with relationships
3. **Phase 3-7 (API)**: Implement REST endpoints for each feature area
4. **Phase 8 (Dashboard)**: Aggregation endpoints for dashboard
5. **Phase 9 (Frontend)**: Vanilla JS SPA with all views
6. **Phase 10 (Testing)**: Comprehensive test suite with 95% coverage

---

## Notes

- Greenfield project - building from scratch
- Python 3.10+ required
- Flask for backend API
- SQLAlchemy ORM with SQLite
- Vanilla JavaScript frontend
- Chart.js for data visualization
- pytest for testing (95% coverage target)

---

## Next Iteration

Start with **TASK-004** (create backend directory structure) as it's the first incomplete task in Phase 1.
This unblocks all subsequent model and API development.
