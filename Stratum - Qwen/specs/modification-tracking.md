# Modification Tracking Specification

**Related to:** JTBD-002

**Last Updated:** 2026-02-23

---

## Overview

The modification tracking system allows users to document all vehicle modifications with a status workflow, cost tracking, and parts documentation.

---

## Basic Capability

### Modification Entity

**Fields:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `name` (string, e.g., "Stage 1 Tune")
- `description` (text, optional)
- `status` (string: "planned", "in_progress", "completed")
- `cost` (decimal, default 0)
- `installed_date` (date, optional)
- `mileage_at_install` (integer, optional)
- `notes` (text, optional, installation notes)
- `vendor` (string, optional)
- `vendor_url` (string, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### CRUD Operations

**Create Modification:**
- Endpoint: `POST /api/mods`
- Required fields: `vehicle_id`, `name`
- Optional fields: all others
- Default status: "planned"
- Returns: Created modification object

**Read Modifications:**
- List all: `GET /api/mods`
- Filter by vehicle: `GET /api/mods?vehicle_id=<id>`
- Filter by status: `GET /api/mods?status=completed`
- Get one: `GET /api/mods/<id>`
- Returns: Modification object(s)

**Update Modification:**
- Endpoint: `PUT /api/mods/<id>`
- Accepts: Any modification fields
- Returns: Updated modification object

**Delete Modification:**
- Endpoint: `DELETE /api/mods/<id>`
- Returns: 204 No Content

---

## Enhanced Capability

### Parts Tracking

**Field:**
- `parts` (text, stored as JSON array)

**Format:**
```json
[
  {"name": "Downpipe", "part_number": "DP-200", "cost": 450.00, "vendor": "IE"},
  {"name": "Intercooler", "part_number": "IC-500", "cost": 850.00, "vendor": "034"}
]
```

**Storage:**
- Stored as JSON text in database
- Serialized/deserialized automatically in API
- Total cost can be calculated from parts or set manually

### Status Workflow

**Valid Statuses:**
- `planned`: Modification is planned but not started
- `in_progress`: Modification is being installed
- `completed`: Modification is fully installed

**Status Transitions:**
```
planned → in_progress → completed
  ↓         ↓           ↓
  └─────────┴───────────┘
       (can go back)
```

**Update Status:**
- Endpoint: `PUT /api/mods/<id>/status`
- Body: `{"status": "in_progress"}`
- Validation: Must be valid status value
- Returns: Updated modification object

**Status Change History (Optional Enhancement):**
- Track when status changes occurred
- Store in separate `mod_status_history` table
- Fields: `mod_id`, `old_status`, `new_status`, `changed_at`

### Cost Aggregation

**Mod Cost Calculation:**
- If `parts` JSON exists, sum the `cost` fields
- Otherwise use the `cost` field directly
- Store both individual part costs and total

**Dashboard Aggregation:**
- Endpoint: `GET /api/dashboard`
- Include in response:
```json
{
  "total_mods": 12,
  "total_mod_cost": 5420.50,
  "mods_by_status": {
    "planned": {"count": 4, "cost": 2000.00},
    "in_progress": {"count": 2, "cost": 500.00},
    "completed": {"count": 6, "cost": 2920.50}
  }
}
```

---

## Advanced Capability

### Status Filtering

**Filter by Status:**
- Endpoint: `GET /api/mods?status=completed`
- Multiple statuses: `GET /api/mods?status=planned,in_progress`
- Combine with vehicle filter: `GET /api/mods?vehicle_id=1&status=completed`

**Status Filter Implementation:**
```python
@app.route('/api/mods', methods=['GET'])
def get_mods():
    vehicle_id = request.args.get('vehicle_id')
    status = request.args.get('status')
    
    query = Modification.query
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    if status:
        statuses = status.split(',')
        query = query.filter(Modification.status.in_(statuses))
    
    return jsonify(query.all())
```

### Mod Timeline

**Get Mod Installation Timeline:**
- Endpoint: `GET /api/mods/timeline?vehicle_id=<id>`
- Returns: Modifications sorted by installed_date
- Only includes mods with `status=completed` and `installed_date`

**Timeline Item:**
```json
{
  "id": 5,
  "name": "Stage 1 Tune",
  "installed_date": "2024-03-15",
  "mileage_at_install": 35000,
  "cost": 650.00,
  "notes": "Installed by APR dealer"
}
```

### Cost Analysis

**Mod Cost Summary:**
- Endpoint: `GET /api/mods/summary?vehicle_id=<id>`
- Returns:
```json
{
  "total_mods": 12,
  "completed_mods": 6,
  "total_cost": 5420.50,
  "completed_cost": 2920.50,
  "planned_cost": 2000.00,
  "in_progress_cost": 500.00,
  "cost_by_category": {
    "Engine": 2500.00,
    "Suspension": 1200.00,
    "Wheels": 850.00,
    "Exterior": 870.50
  }
}
```

**Category Field (Optional):**
- Add `category` field to modification entity
- Categories: Engine, Suspension, Wheels, Brakes, Exterior, Interior, Audio, Other

---

## Acceptance Criteria

### Basic

- [ ] Create modification with vehicle_id and name
- [ ] Update any modification field
- [ ] Delete modification
- [ ] List all modifications
- [ ] Filter by vehicle_id
- [ ] Get single modification details
- [ ] Validate required fields
- [ ] Return 404 for non-existent modification

### Enhanced

- [ ] Store parts as JSON array
- [ ] Retrieve parts as parsed JSON
- [ ] Update modification status through workflow
- [ ] Validate status values (planned/in_progress/completed)
- [ ] Calculate total cost from parts
- [ ] Include mod costs in dashboard aggregation
- [ ] Show mods grouped by status in dashboard

### Advanced

- [ ] Filter modifications by status
- [ ] Support multiple status filters
- [ ] Combine status filter with vehicle filter
- [ ] Timeline shows completed mods by install date
- [ ] Cost summary aggregates by category
- [ ] Cascade delete when vehicle deleted

---

## Edge Cases

### Validation

- Name cannot be empty
- Cost cannot be negative
- Mileage at install cannot be negative
- Installed date cannot be in the future
- Status must be one of: planned, in_progress, completed
- Vendor URL must be valid URL if provided

### Parts JSON

- If parts array is empty, use cost field
- If parts array has items, sum costs automatically
- Handle missing cost in part (default to 0)
- Validate part structure (name required)

### Status Workflow

- Allow any status transition (no restrictions)
- When status changes to "completed", prompt for installed_date
- When status changes from "completed", clear installed_date (optional)

---

## Data Relationships

```
Vehicle (1) ──→ (many) Modification
```

---

## API Response Format

### Modification Object

```json
{
  "id": 1,
  "vehicle_id": 1,
  "name": "Stage 1 Tune",
  "description": "APR Stage 1 ECU tune",
  "status": "completed",
  "cost": 650.00,
  "installed_date": "2024-03-15",
  "mileage_at_install": 35000,
  "notes": "Installed by APR dealer, required 93 octane",
  "vendor": "APR",
  "vendor_url": "https://goapr.com",
  "parts": [
    {"name": "ECU Tune", "part_number": "TR-200", "cost": 650.00, "vendor": "APR"}
  ],
  "created_at": "2024-02-01T10:00:00Z",
  "updated_at": "2024-03-15T16:30:00Z"
}
```

### Dashboard Mods Summary

```json
{
  "total_mods": 12,
  "total_mod_cost": 5420.50,
  "mods_by_status": {
    "planned": {"count": 4, "cost": 2000.00},
    "in_progress": {"count": 2, "cost": 500.00},
    "completed": {"count": 6, "cost": 2920.50}
  }
}
```

---

## Notes

- Modifications are optional (user can track or not)
- Status workflow helps track installation progress
- Parts tracking optional (can just use total cost)
- Vendor information helps with warranty/reordering
