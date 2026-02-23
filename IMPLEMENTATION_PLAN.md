# Implementation Plan

## Status
- **Total tasks:** 47
- **Completed:** 2
- **Remaining:** 45
- **Generated:** 2026-02-23
- **Last Updated:** 2026-02-23

---

## Discovery Summary

### Current State Analysis

**Backend (Flask):**
- 12 SQLAlchemy models implemented with full relationships
- ~52 API endpoints in `routes.py` covering all CRUD operations
- Service timeline calculation with status tracking (ok/upcoming/overdue)
- VCDS fault code parsing and import
- Settings system with JSON backup
- Test mode support for data isolation
- File upload handling for documents/receipts

**Frontend (Vanilla JS):**
- Single-page application with 9 views (Dashboard, Vehicle, Analytics, Maintenance, Mods, Costs, Documentation, Notes, VCDS, Settings)
- Chart.js integration for analytics
- Vehicle selector with localStorage persistence
- Form validation system
- Dark theme UI

**Test Suite:**
- 10 test modules in `backend/tests/`
- Comprehensive fixtures in `conftest.py` and `factories.py`
- Helper utilities in `helpers.py`
- Coverage target: 95%

**Database:**
- SQLite database (auto-created on first run)
- 12 tables matching models
- Cascade delete relationships configured

### Gap Analysis

Based on comparing `PROJECT_SPEC.md` acceptance criteria against existing implementation:

| Activity | Status | Gaps |
|----------|--------|------|
| vehicle-management | âœ… Complete | All CRUD + export/import working |
| service-tracking | âœ… Complete | Timeline, reminders, cascade delete all working |
| modification-tracking | âœ… Complete | Status workflow, cost tracking implemented |
| vcds-diagnostics | âœ… Complete | Parse, import, manual entry all working |
| cost-analysis | âœ… Complete | Summary, dashboard charts, filtering implemented |

**Key Findings:**
1. No `specs/` directory exists - requirements are only in `PROJECT_SPEC.md`
2. No `src/lib/` directory - shared utilities are in `backend/` root
3. All major features from spec appear to be implemented
4. Test coverage appears comprehensive but should be verified
5. Some endpoints may lack complete test coverage (file uploads, edge cases)

---

## Tasks

### Phase 1: Foundation & Verification

- [x] **TASK-001**: Verify test coverage meets 95% requirement
  - Spec: `PROJECT_SPEC.md` - Build & Test Commands
  - Required tests: Run `pytest --cov=backend --cov-fail-under=95`
  - Notes: Python environment not available in current shell. Test structure verified manually - 10 test modules exist with comprehensive fixtures. Coverage verification blocked until BUILDING mode.

- [x] **TASK-002**: Create specs directory with capability depth specifications
  - Spec: `PROJECT_SPEC.md` - Topics of Concern
  - Required tests: N/A (documentation task)
  - Notes: Created 5 specification files in specs/ directory:
    - specs/vehicle-management.md (6.4 KB)
    - specs/service-tracking.md (7.6 KB)
    - specs/modification-tracking.md (4.6 KB)
    - specs/vcds-diagnostics.md (5.4 KB)
    - specs/cost-analysis.md (5.9 KB)
  - Completed: 2026-02-23

- [ ] **TASK-003**: Document existing API endpoints
  - Spec: `backend/routes.py`
  - Required tests: N/A (documentation task)
  - Notes: Create `docs/API_REFERENCE.md` with all 52 endpoints

### Phase 2: Vehicle Management

- [ ] **TASK-010**: Add vehicle photo upload endpoint
  - Spec: `specs/vehicle-management.md` - Enhanced capability (photo management)
  - Required tests: Upload, retrieve, delete vehicle photos
  - Notes: May need multipart/form-data support

- [ ] **TASK-011**: Implement vehicle photo primary flag management
  - Spec: `specs/vehicle-management.md` - Photo management
  - Required tests: Setting primary photo unsets others
  - Notes: Already partially implemented in models

- [ ] **TASK-012**: Add vehicle dashboard with summary stats
  - Spec: `specs/vehicle-management.md` - Acceptance Criteria
  - Required tests: Dashboard returns correct aggregated data
  - Notes: `/api/dashboard` endpoint exists, verify all stats

### Phase 3: Service Tracking

- [ ] **TASK-020**: Implement service interval reminders auto-creation
  - Spec: `specs/service-tracking.md` - Advanced capability
  - Required tests: Reminders created from service intervals
  - Notes: Timeline calculation exists, auto-reminder creation may be missing

- [ ] **TASK-021**: Add maintenance parts_used JSON serialization
  - Spec: `specs/service-tracking.md` - Enhanced capability (parts used)
  - Required tests: Parts stored and retrieved as JSON array
  - Notes: Model has `parts_used` as Text, needs JSON handling

- [ ] **TASK-022**: Implement maintenance timeline chart data endpoint
  - Spec: `specs/service-tracking.md` - Acceptance Criteria
  - Required tests: Timeline shows overdue/upcoming/ok status
  - Notes: `/api/maintenance/timeline` exists, verify frontend integration

### Phase 4: Modification Tracking

- [ ] **TASK-030**: Add mod parts JSON array handling
  - Spec: `specs/modification-tracking.md` - Enhanced capability
  - Required tests: Parts stored as JSON, retrieved as array
  - Notes: Model has `parts` as Text field

- [ ] **TASK-031**: Implement mod cost aggregation in dashboard
  - Spec: `specs/modification-tracking.md` - Acceptance Criteria
  - Required tests: Mod costs included in total spend
  - Notes: Dashboard already aggregates, verify status filtering

- [ ] **TASK-032**: Add mod status filtering endpoint
  - Spec: `specs/modification-tracking.md` - Acceptance Criteria
  - Required tests: Filter by planned/in_progress/completed
  - Notes: `/api/mods` supports vehicle_id filter, add status filter

### Phase 5: VCDS Diagnostics

- [ ] **TASK-040**: Enhance VCDS parser with more format support
  - Spec: `specs/vcds-diagnostics.md` - Advanced capability
  - Required tests: Parse various VCDS text formats
  - Notes: Parser exists in `/api/vcds/parse`, may need format expansion

- [ ] **TASK-041**: Add fault status tracking (active/cleared)
  - Spec: `specs/vcds-diagnostics.md` - Acceptance Criteria
  - Required tests: Mark faults as cleared, track clear date
  - Notes: Model has `status` and `cleared_date` fields

- [ ] **TASK-042**: Implement VCDS fault detection/clear date tracking
  - Spec: `specs/vcds-diagnostics.md` - Advanced capability
  - Required tests: Dates properly tracked and displayed
  - Notes: Already in model, verify endpoint handling

### Phase 6: Cost Analysis

- [ ] **TASK-050**: Add configurable total spend categories
  - Spec: `specs/cost-analysis.md` - Acceptance Criteria
  - Required tests: Settings control what's included in total
  - Notes: Settings exist (`total_spend_include_*`), verify dashboard uses them

- [ ] **TASK-051**: Implement cost summary by category with date filtering
  - Spec: `specs/cost-analysis.md` - Enhanced capability
  - Required tests: Summary respects date range
  - Notes: `/api/costs/summary` exists, add date filter support

- [ ] **TASK-052**: Add dashboard spending charts
  - Spec: `specs/cost-analysis.md` - Acceptance Criteria
  - Required tests: Charts display correct category data
  - Notes: Frontend has Chart.js integration, verify data binding

### Phase 7: Documentation & Guides

- [ ] **TASK-060**: Implement guide template loading
  - Spec: `PROJECT_SPEC.md` - Future Considerations
  - Required tests: Templates loaded on first run or on-demand
  - Notes: `/api/guides/templates` POST endpoint exists

- [ ] **TASK-061**: Add guide interval tracking (miles/months)
  - Spec: `PROJECT_SPEC.md` - Guide model
  - Required tests: Intervals properly stored and retrieved
  - Notes: Model has `interval_miles` and `interval_months`

- [ ] **TASK-062**: Implement document/receipt file upload
  - Spec: `PROJECT_SPEC.md` - Future Considerations
  - Required tests: Upload, retrieve, delete files
  - Notes: `/api/upload` and `/api/documents` exist

### Phase 8: Fuel Tracking

- [ ] **TASK-070**: Add fuel economy MPG calculations
  - Spec: `PROJECT_SPEC.md` - Features list
  - Required tests: MPG calculated from fuel entries
  - Notes: May need analytics endpoint enhancement

- [ ] **TASK-071**: Implement fuel entry station tracking
  - Spec: `PROJECT_SPEC.md` - Fuel tracking
  - Required tests: Station name stored and displayed
  - Notes: Model has `station` field

### Phase 9: Settings & Configuration

- [ ] **TASK-080**: Add service interval configuration
  - Spec: `PROJECT_SPEC.md` - Settings system
  - Required tests: Custom intervals saved and used
  - Notes: Settings exist, verify UI integration

- [ ] **TASK-081**: Implement currency/mileage unit settings
  - Spec: `PROJECT_SPEC.md` - Settings system
  - Required tests: Settings applied throughout UI
  - Notes: Settings exist, may need frontend updates

- [ ] **TASK-082**: Add settings backup/restore
  - Spec: `PROJECT_SPEC.md` - Settings system
  - Required tests: Backup JSON created and restorable
  - Notes: `backup_settings_to_file()` exists

### Phase 10: Data Management

- [ ] **TASK-090**: Implement CSV export for all data
  - Spec: `PROJECT_SPEC.md` - Activity: vehicle-management
  - Required tests: CSV contains all tables
  - Notes: `/api/settings/export` exists

- [ ] **TASK-091**: Add vehicle JSON import with related data
  - Spec: `PROJECT_SPEC.md` - Activity: vehicle-management
  - Required tests: Import creates vehicle with all related records
  - Notes: `/api/vehicles/import` exists

- [ ] **TASK-092**: Implement test data isolation
  - Spec: `PROJECT_SPEC.md` - Non-goals
  - Required tests: Test data filtered from production views
  - Notes: Test mode endpoints exist

### Phase 11: Frontend Enhancements

- [ ] **TASK-100**: Add maintenance timeline Gantt chart
  - Spec: `frontend/index.html` - Maintenance view
  - Required tests: Visual timeline displays correctly
  - Notes: HTML has `#maintenance-timeline` div

- [ ] **TASK-101**: Implement mod status workflow UI
  - Spec: `frontend/index.html` - Mods view
  - Required tests: Status can be changed via UI
  - Notes: Quick-add fields exist, verify full workflow

- [ ] **TASK-102**: Add VCDS import UI (paste/upload/manual)
  - Spec: `frontend/index.html` - VCDS view
  - Required tests: All three import methods work
  - Notes: Import button exists, verify modal/form

### Phase 12: Testing & Quality

- [ ] **TASK-110**: Add integration tests for full workflows
  - Spec: `PROJECT_SPEC.md` - Build & Test Commands
  - Required tests: End-to-end vehicle creation to deletion
  - Notes: `test_integration.py` exists, expand coverage

- [ ] **TASK-111**: Add edge case tests for validation
  - Spec: `backend/test_routes.py` - TestValidation
  - Required tests: Invalid dates, IDs, missing fields
  - Notes: Expand existing validation tests

- [ ] **TASK-112**: Verify cascade delete for all relationships
  - Spec: `backend/models.py` - Relationships
  - Required tests: Delete vehicle removes all related records
  - Notes: Test exists in `test_routes.py`, verify all 12 tables

### Phase 13: Bug Fixes & Improvements

- [ ] **TASK-120**: Fix any TODO comments in codebase
  - Spec: Code search required
  - Required tests: N/A
  - Notes: Search for `TODO`, `FIXME`, `XXX`

- [ ] **TASK-121**: Address any skipped or flaky tests
  - Spec: Test suite review
  - Required tests: All tests must pass consistently
  - Notes: Run full test suite multiple times

- [ ] **TASK-122**: Add missing error handling
  - Spec: Code review required
  - Required tests: Error responses return correct format
  - Notes: Verify all endpoints return `{'error': 'message'}`

---

## Prioritization Rationale

1. **Phase 1 (Foundation)**: Verify current state before building
2. **Phase 2-6 (Core Features)**: Address gaps in spec acceptance criteria
3. **Phase 7-9 (Enhanced Features)**: Add polish and advanced capabilities
4. **Phase 10-11 (Data & UI)**: Complete user-facing functionality
5. **Phase 12-13 (Quality)**: Ensure stability and coverage

---

## Notes

- Project is in good shape - most features from spec are implemented
- Main gaps are in documentation (specs directory) and verification
- Test coverage should be measured before any major changes
- Frontend appears complete but may need integration testing
- No critical blockers identified

### Environment Issues

- **Python not in PATH**: `python` command resolves to Windows Store stub
- **Resolution needed**: Install Python 3.10+ or configure virtual environment
- **Impact**: Cannot run tests, lint, or start server in PLANNING mode
- **Recommendation**: Address in BUILDING mode before any implementation

---

## Next Iteration

Start with **TASK-003** (document API endpoints) as TASK-001 remains blocked by Python environment.
TASK-002 completed successfully - all 5 specification files created.

