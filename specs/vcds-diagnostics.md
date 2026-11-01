# VCDS Diagnostics Specification

**Related to:** JTBD-002 (VCDS fault code tracking)

**Description:** Import, parse, and track VCDS fault code scans. Support manual entry, text paste parsing, and file upload. Track fault status and clear dates.

---

## Capability Depths

### Basic

Minimal viable implementation for VCDS tracking:

- Manual fault code entry with:
  - Address (e.g., "01-Engine")
  - Fault code (e.g., "P0300")
  - Description
  - Status (active/cleared)
- View faults filtered by vehicle
- Delete faults

### Enhanced

Additional features for comprehensive tracking:

- Parse VCDS text format from clipboard paste
- Upload .txt/.csv files for import
- Fault status tracking (active/cleared)
- Detection date tracking
- Clear date tracking
- Notes field for additional details

### Advanced

Edge cases and integrations:

- Enhanced VCDS parser with multiple format support
- Fault history tracking
- Recurring fault detection
- Component name extraction

---

## Data Model

### VCDSFault Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| address | String(50) | | Control module address (e.g., "01-Engine") |
| component | String(200) | | Component name |
| fault_code | String(20) | | DTC code (e.g., "P0300") |
| description | Text | | Fault description |
| status | String(20) | Default: 'active' | active/cleared |
| detected_date | Date | | Date fault was detected |
| cleared_date | Date | | Date fault was cleared |
| notes | Text | | Additional notes |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

---

## API Endpoints

### VCDS Fault CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vcds?vehicle_id= | List VCDS faults |
| POST | /api/vcds | Create fault manually |
| GET | /api/vcds/{id} | Get fault by ID |
| PUT | /api/vcds/{id} | Update fault (mark cleared, etc.) |
| DELETE | /api/vcds/{id} | Delete fault |

### VCDS Import

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/vcds/parse | Parse VCDS text from clipboard |
| POST | /api/vcds/import | Import from file upload |

---

## Acceptance Criteria

### Core Functionality

- [ ] Can create fault manually with all fields (address, component, fault_code, description, status, detected_date, notes)
- [ ] Can retrieve faults filtered by vehicle_id
- [ ] Can update fault (including marking as cleared)
- [ ] Can delete fault
- [ ] Faults sorted by detected_date descending

### VCDS Text Parsing

- [ ] Can paste VCDS scan text and auto-parse
- [ ] Parser extracts:
  - Address (e.g., "Address 01: Engine")
  - Component (e.g., "2.0L R4/4V TDI")
  - Fault codes (e.g., "000268 - Idle Air Control System")
  - Descriptions
- [ ] Parser handles standard VCDS text format
- [ ] Parsed faults can be reviewed before saving
- [ ] Multiple faults from single scan supported

### File Import

- [ ] Can upload .txt file for import
- [ ] Can upload .csv file for import
- [ ] File parsed using same parser as text paste
- [ ] Import validates vehicle_id before saving
- [ ] Import returns count of faults imported

### Fault Status Tracking

- [ ] Status defaults to 'active' on creation
- [ ] Can mark fault as 'cleared' via update
- [ ] cleared_date set when status changed to 'cleared'
- [ ] Can filter faults by status:
  - GET /api/vcds?vehicle_id=1&status=active returns only active faults
  - GET /api/vcds?vehicle_id=1&status=cleared returns only cleared faults
- [ ] Cleared faults remain in history (not deleted)

### Date Tracking

- [ ] detected_date stored when fault created
- [ ] cleared_date stored when fault marked as cleared
- [ ] Dates displayed in UI
- [ ] Dates use ISO format (YYYY-MM-DD)

### Validation & Error Handling

- [ ] Fault creation validates required fields (vehicle_id, fault_code)
- [ ] Invalid fault ID returns 404
- [ ] All error responses return {'error': 'message'} format
- [ ] Date format validated (YYYY-MM-DD)
- [ ] Status validation: only accepts active/cleared

---

## VCDS Text Format Example

Standard VCDS output format:

`
VCDS Version: 21.3.0
VIN: WVWZZZ1KZBW123456

Address 01: Engine
  Component: 2.0L R4/4V TDI
  Fault Code: 000268
  Description: Idle Air Control System: P0505-00 - Malfunction
  Status: Active
  Detected: 2024-01-15

Address 03: ABS Brakes
  Component: ESP Mk70
  Fault Code: 01234
  Description: Wheel Speed Sensor: Front Left
  Status: Cleared
  Detected: 2024-01-10
  Cleared: 2024-01-12
`

---

## Frontend Integration

### VCDS View

- Faults list with filter by vehicle and status
- Manual fault entry form
- VCDS text paste area (textarea)
- File upload button (.txt/.csv)
- Parse preview before saving
- Mark as cleared button
- Fault detail display

### Dashboard View

- Active fault count
- Recent faults list
- Fault status summary (active vs cleared)

---

## Notes

- Parser located in /api/vcds/parse endpoint
- Supports both text paste and file upload
- Faults remain in history even when cleared (soft delete via status)
- Test mode support via test_key field for data isolation
- Component name extraction may vary by VCDS version
