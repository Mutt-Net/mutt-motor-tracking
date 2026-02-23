# Modification Tracking Specification

**Related to:** JTBD-003 (Modification planning and tracking)

**Description:** Track vehicle modifications through their lifecycle from planned to completed. Manage parts lists, costs, and installation dates.

---

## Capability Depths

### Basic

Minimal viable implementation for modification tracking:

- Create mod records with:
  - Description
  - Status (planned/in_progress/completed)
  - Category (e.g., performance, aesthetic, audio)
- View mods sorted by date
- Filter by vehicle and status

### Enhanced

Additional features for comprehensive tracking:

- Parts list (stored as JSON array)
- Cost tracking per mod
- Installation date tracking
- Mileage at installation
- Notes field for details

### Advanced

Edge cases and integrations:

- Cost analysis by category
- Mod timeline visualization
- Status workflow management
- Mod costs aggregated in dashboard total spend

---

## Data Model

### Mod Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| date | Date | | Installation/completion date |
| mileage | Integer | | Odometer at installation |
| category | String(50) | | Mod category (performance, aesthetic, etc.) |
| description | Text | | Mod description |
| parts | Text | | JSON array of parts used |
| cost | Float | | Total cost |
| status | String(20) | Default: 'planned' | planned/in_progress/completed |
| notes | Text | | Additional notes |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

---

## API Endpoints

### Mod CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/mods?vehicle_id=&status= | List mods (filter by vehicle and status) |
| POST | /api/mods | Create mod record |
| GET | /api/mods/{id} | Get mod by ID |
| PUT | /api/mods/{id} | Update mod record |
| DELETE | /api/mods/{id} | Delete mod record |

---

## Acceptance Criteria

### Core Functionality

- [ ] Can create mod with all fields (description, status, category, date, mileage, parts, cost, notes)
- [ ] Can retrieve mods filtered by vehicle_id
- [ ] Can filter mods by status (planned/in_progress/completed)
- [ ] Can update mod record including status changes
- [ ] Can delete mod record
- [ ] Mods sorted by date descending

### Parts Tracking

- [ ] Parts stored as JSON array in parts field
- [ ] Parts retrieved as array from JSON
- [ ] Can add/edit parts list via JSON

### Status Workflow

- [ ] Status defaults to 'planned' on creation
- [ ] Status can be changed to 'in_progress'
- [ ] Status can be changed to 'completed'
- [ ] Status filtering works correctly:
  - GET /api/mods?status=planned returns only planned mods
  - GET /api/mods?status=in_progress returns only in-progress mods
  - GET /api/mods?status=completed returns only completed mods
  - GET /api/mods?vehicle_id=1&status=completed returns completed mods for vehicle 1

### Cost Tracking

- [ ] Cost stored as float
- [ ] Mod costs included in dashboard total spend calculation
- [ ] Dashboard respects settings for what's included in total spend
- [ ] Cost aggregation works across all mods for a vehicle

### Validation & Error Handling

- [ ] Mod creation validates required fields (vehicle_id, description)
- [ ] Invalid mod ID returns 404
- [ ] All error responses return {'error': 'message'} format
- [ ] Date format validated (YYYY-MM-DD)
- [ ] Status validation: only accepts planned/in_progress/completed

---

## Status Values

| Status | Description |
|--------|-------------|
| planned | Mod is planned but not yet started |
| in_progress | Mod is currently being installed |
| completed | Mod installation is complete |

---

## Frontend Integration

### Mods View

- Mods list with filter by vehicle and status
- Add/edit mod form with all fields
- Parts as JSON array input
- Status dropdown selector
- Quick-add fields for rapid entry
- Mod cost display

### Dashboard View

- Total mod cost aggregation
- Mods by status summary (counts)
- Recent mods list
- Mod costs included in total spend chart

---

## Notes

- Parts stored as JSON text, serialized/deserialized in route handlers
- Status workflow enables tracking mod progress over time
- Mod costs aggregated in dashboard along with maintenance, fuel, and other costs
- Test mode support via test_key field for data isolation
- Category is free-form text (no predefined categories enforced)
