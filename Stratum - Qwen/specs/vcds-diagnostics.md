# VCDS Diagnostics Specification

**Related to:** JTBD-003

**Last Updated:** 2026-02-23

---

## Overview

The VCDS diagnostics system allows users to parse, import, and track fault codes from VAG-COM/VCDS diagnostic scans. It supports manual entry, text parsing, and status tracking.

---

## Basic Capability

### Fault Code Entity

**Fields:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `fault_code` (string, e.g., "P0301")
- `description` (text)
- `ecu` (string, optional, e.g., "Engine Control Module")
- `status` (string: "active", "cleared")
- `detected_date` (date)
- `cleared_date` (date, optional)
- `notes` (text, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### CRUD Operations

**Create Fault Code:**
- Endpoint: `POST /api/vcds`
- Required fields: `vehicle_id`, `fault_code`, `description`
- Optional fields: all others
- Default status: "active"
- Returns: Created fault code object

**Read Fault Codes:**
- List all: `GET /api/vcds`
- Filter by vehicle: `GET /api/vcds?vehicle_id=<id>`
- Filter by status: `GET /api/vcds?status=active`
- Get one: `GET /api/vcds/<id>`
- Returns: Fault code object(s)

**Update Fault Code:**
- Endpoint: `PUT /api/vcds/<id>`
- Accepts: Any fault code fields
- Returns: Updated fault code object

**Delete Fault Code:**
- Endpoint: `DELETE /api/vcds/<id>`
- Returns: 204 No Content

---

## Enhanced Capability

### VCDS Text Parsing

**Parse VCDS Output:**
- Endpoint: `POST /api/vcds/parse`
- Content-Type: `application/json` or `text/plain`
- Body: Raw VCDS text output
- Returns: Parsed fault codes array

**VCDS Format Example:**
```
Address 01: Engine
Fault Codes:
1 Fault Found:
000768 - Random/Multiple Cylinder Misfire Detected
P0300 - 000 - - Intermittent
Freeze Frame:
RPM: 850 /min
Load: 23.5 %
```

**Parser Requirements:**
- Extract fault code (e.g., "P0300")
- Extract description (e.g., "Random/Multiple Cylinder Misfire Detected")
- Extract ECU address (e.g., "Engine")
- Extract status indicators (Intermittent, Sporadic, etc.)
- Handle multiple fault codes in one scan
- Handle multiple ECUs in one scan

**Parsed Result:**
```json
[
  {
    "fault_code": "P0300",
    "description": "Random/Multiple Cylinder Misfire Detected",
    "ecu": "Engine",
    "status_extra": "Intermittent"
  }
]
```

### Import Parsed Codes

**Import Fault Codes:**
- Endpoint: `POST /api/vcds/import`
- Body:
```json
{
  "vehicle_id": 1,
  "scan_date": "2024-06-15",
  "faults": [
    {
      "fault_code": "P0300",
      "description": "Random/Multiple Cylinder Misfire Detected",
      "ecu": "Engine"
    }
  ]
}
```
- Behavior: Creates fault codes for vehicle
- Returns: Array of created fault code objects

**Import Options:**
- `skip_existing` (boolean, default false): Don't create if code already exists
- `update_existing` (boolean, default false): Update description if code exists

---

## Advanced Capability

### Fault Status Tracking

**Status Values:**
- `active`: Fault is currently present
- `cleared`: Fault has been cleared/resolved

**Clear Fault Code:**
- Endpoint: `PUT /api/vcds/<id>/clear`
- Body: `{"cleared_date": "2024-06-20"}` (optional, defaults to today)
- Behavior: Sets status to "cleared", records cleared_date
- Returns: Updated fault code object

**Reactivate Fault Code:**
- Endpoint: `PUT /api/vcds/<id>/activate`
- Behavior: Sets status to "active", clears cleared_date
- Returns: Updated fault code object

**Status History (Optional Enhancement):**
- Track status changes in separate table
- Fields: `fault_id`, `old_status`, `new_status`, `changed_at`

### Detection and Clear Date Tracking

**Detected Date:**
- Set when fault is first created or imported
- Updated if fault reappears after being cleared
- Format: ISO 8601 date (YYYY-MM-DD)

**Cleared Date:**
- Set when fault is marked as cleared
- Cleared when fault status changes to "cleared"
- Format: ISO 8601 date (YYYY-MM-DD)

**Fault Age Calculation:**
- Calculate days between detected_date and cleared_date
- Show in UI as "Active for X days" or "Cleared after X days"

### Fault Code History

**Get Fault History:**
- Endpoint: `GET /api/vcds/history?vehicle_id=<id>`
- Includes: Both active and cleared faults
- Sort: By detected_date descending
- Returns: Array of fault codes

**Fault Recurrence Tracking:**
- Track how many times a fault code has appeared
- Count based on fault_code + vehicle_id
- Show in UI as "This fault has occurred 3 times"

**Recurrence Calculation:**
```python
def get_fault_recurrence(vehicle_id, fault_code):
    count = FaultCode.query.filter_by(
        vehicle_id=vehicle_id,
        fault_code=fault_code
    ).count()
    return count
```

### Fault Statistics

**Get Fault Summary:**
- Endpoint: `GET /api/vcds/summary?vehicle_id=<id>`
- Returns:
```json
{
  "total_faults": 15,
  "active_faults": 3,
  "cleared_faults": 12,
  "faults_by_ecu": {
    "Engine": 8,
    "Transmission": 4,
    "ABS": 3
  },
  "most_common_faults": [
    {"fault_code": "P0300", "count": 3, "description": "Misfire"},
    {"fault_code": "P0420", "count": 2, "description": "Catalyst Efficiency"}
  ]
}
```

---

## Acceptance Criteria

### Basic

- [ ] Create fault code manually with required fields
- [ ] Update fault code details
- [ ] Delete fault code
- [ ] List all fault codes
- [ ] Filter by vehicle_id
- [ ] Filter by status (active/cleared)
- [ ] Get single fault code details
- [ ] Validate required fields
- [ ] Return 404 for non-existent fault code

### Enhanced

- [ ] Parse VCDS text output into structured faults
- [ ] Extract fault code, description, ECU from text
- [ ] Handle multiple faults in one scan
- [ ] Handle multiple ECUs in one scan
- [ ] Import parsed faults to database
- [ ] Support skip_existing option
- [ ] Support update_existing option

### Advanced

- [ ] Mark fault as cleared with date
- [ ] Mark fault as active (reactivate)
- [ ] Track detected_date accurately
- [ ] Track cleared_date accurately
- [ ] Calculate fault age (days active)
- [ ] Get fault history (includes cleared)
- [ ] Track fault recurrence count
- [ ] Generate fault summary statistics
- [ ] Cascade delete when vehicle deleted

---

## Edge Cases

### Validation

- Fault code cannot be empty
- Fault code format: typically 5 characters (e.g., P0300)
- Description cannot be empty
- Detected date cannot be in the future
- Cleared date cannot be before detected date
- Status must be "active" or "cleared"

### Parsing Edge Cases

- Handle VCDS output with no faults found
- Handle malformed VCDS output gracefully
- Handle unknown fault code formats
- Handle missing ECU information
- Handle special characters in descriptions

### Import Behavior

- If skip_existing=true, don't create duplicate fault_code for same vehicle
- If update_existing=true, update description but keep dates
- Default behavior: create new fault code (allows tracking recurrence)

---

## Data Relationships

```
Vehicle (1) ──→ (many) FaultCode
```

---

## API Response Format

### Fault Code Object

```json
{
  "id": 1,
  "vehicle_id": 1,
  "fault_code": "P0300",
  "description": "Random/Multiple Cylinder Misfire Detected",
  "ecu": "Engine Control Module",
  "status": "active",
  "detected_date": "2024-06-15",
  "cleared_date": null,
  "notes": "Intermittent misfire at idle",
  "created_at": "2024-06-15T10:30:00Z",
  "updated_at": "2024-06-15T10:30:00Z"
}
```

### Parsed Faults Response

```json
[
  {
    "fault_code": "P0300",
    "description": "Random/Multiple Cylinder Misfire Detected",
    "ecu": "Engine",
    "status_extra": "Intermittent"
  },
  {
    "fault_code": "P0420",
    "description": "Catalyst System Efficiency Below Threshold",
    "ecu": "Engine",
    "status_extra": null
  }
]
```

### Fault Summary Response

```json
{
  "total_faults": 15,
  "active_faults": 3,
  "cleared_faults": 12,
  "faults_by_ecu": {
    "Engine": 8,
    "Transmission": 4,
    "ABS": 3
  },
  "most_common_faults": [
    {"fault_code": "P0300", "count": 3, "description": "Misfire"},
    {"fault_code": "P0420", "count": 2, "description": "Catalyst Efficiency"}
  ]
}
```

---

## Notes

- VCDS parsing is best-effort (format varies by version)
- Fault codes can be manually entered or imported
- Status tracking helps monitor repair progress
- Recurrence tracking identifies persistent issues
