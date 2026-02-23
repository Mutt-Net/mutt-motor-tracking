# Service Tracking Specification

**Related to:** JTBD-001 (Service record tracking)

**Description:** Log maintenance records with cost, parts, labor, and shop information. Track service intervals and timeline status.

---

## Capability Depths

### Basic

Minimal viable implementation for service tracking:

- Create maintenance records with:
  - Date (required)
  - Category (e.g., oil_change, brakes, tire_rotation)
  - Description
  - Cost
- View maintenance history sorted by date descending
- Filter by vehicle

### Enhanced

Additional features for comprehensive tracking:

- Parts used (stored as JSON array)
- Labor hours tracking
- Shop name recording
- Notes field for additional details
- Mileage at time of service

### Advanced

Edge cases and integrations:

- Service interval reminders auto-creation
- Timeline calculations (overdue/upcoming/ok status)
- Service document attachments
- Receipt linking

---

## Data Model

### Maintenance Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| date | Date | Not Null | Service date |
| mileage | Integer | | Odometer at service time |
| category | String(50) | | Service type (oil_change, brakes, etc.) |
| description | Text | | Service description |
| parts_used | Text | | JSON array of parts used |
| labor_hours | Float | | Hours spent on labor |
| cost | Float | | Total cost |
| shop_name | String(100) | | Service provider name |
| notes | Text | | Additional notes |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

### Reminder Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| type | String(50) | Not Null | Reminder type |
| interval_miles | Integer | | Miles between service |
| interval_months | Integer | | Months between service |
| last_service_date | Date | | Last service date |
| last_service_mileage | Integer | | Mileage at last service |
| next_due_date | Date | | Next due date |
| next_due_mileage | Integer | | Mileage when next due |
| notes | Text | | Additional notes |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

### ServiceDocument Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| maintenance_id | Integer | Foreign Key -> maintenance.id (SET NULL) | Related maintenance |
| title | String(200) | Not Null | Document title |
| description | Text | | Document description |
| document_type | String(50) | | Type (receipt, manual, etc.) |
| filename | String(255) | | Stored filename (UUID) |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| uploaded_at | DateTime | Default: UTC now | Upload timestamp |

---

## API Endpoints

### Maintenance CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/maintenance?vehicle_id= | List maintenance records |
| POST | /api/maintenance | Create maintenance record |
| GET | /api/maintenance/{id} | Get maintenance by ID |
| PUT | /api/maintenance/{id} | Update maintenance record |
| DELETE | /api/maintenance/{id} | Delete maintenance record |

### Maintenance Timeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/maintenance/timeline?vehicle_id=&mileage= | Get service timeline status |

### Reminders CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/reminders?vehicle_id= | List reminders |
| POST | /api/reminders | Create reminder |
| PUT | /api/reminders/{id} | Update reminder |
| DELETE | /api/reminders/{id} | Delete reminder |

### Service Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/documents?vehicle_id= | List service documents |
| POST | /api/documents | Upload service document |
| DELETE | /api/documents/{id} | Delete service document |

---

## Acceptance Criteria

### Core Functionality

- [ ] Can create maintenance record with all fields (date, category, description, cost, mileage, parts_used, labor_hours, shop_name, notes)
- [ ] Can retrieve maintenance records filtered by vehicle_id
- [ ] Can update maintenance record
- [ ] Can delete maintenance record
- [ ] Records sorted by date descending

### Parts & Labor Tracking

- [ ] Parts used stored as JSON array in parts_used field
- [ ] Parts retrieved as array from JSON
- [ ] Labor hours stored as float
- [ ] Shop name stored and displayed

### Service Timeline

- [ ] Timeline endpoint accepts vehicle_id and current_mileage
- [ ] Timeline shows status for each service type:
  - oil_change (5000 miles / 6 months)
  - brakes (20000 miles / 24 months)
  - tire_rotation (7500 miles / 6 months)
  - inspection (15000 miles / 12 months)
  - transmission (30000 miles / 24 months)
  - coolant (30000 miles / 24 months)
  - spark_plugs (30000 miles / 36 months)
  - air_filter (15000 miles / 12 months)
  - fuel_filter (30000 miles / 24 months)
- [ ] Status calculation:
  - overdue: past due date OR mileage exceeded
  - upcoming: due within 30 days OR 1000 miles
  - ok: not due soon
- [ ] Timeline includes days_until_due and miles_until_due

### Reminders

- [ ] Can create reminder with interval_miles and/or interval_months
- [ ] Can update reminder with last_service_date and last_service_mileage
- [ ] Next due dates calculated from last service + interval
- [ ] Reminders filtered by vehicle_id

### Service Documents

- [ ] Can upload document with file (multipart/form-data)
- [ ] Document linked to vehicle and optionally to maintenance record
- [ ] Can list documents filtered by vehicle_id
- [ ] Can delete document (removes file from uploads/)
- [ ] Files stored with UUID filenames

### Validation & Error Handling

- [ ] Maintenance creation validates required fields (vehicle_id, date)
- [ ] Invalid maintenance ID returns 404
- [ ] All error responses return {'error': 'message'} format
- [ ] Date format validated (YYYY-MM-DD)

---

## Service Interval Defaults

| Service Type | Miles | Months |
|--------------|-------|--------|
| oil_change | 5000 | 6 |
| brakes | 20000 | 24 |
| tire_rotation | 7500 | 6 |
| inspection | 15000 | 12 |
| transmission | 30000 | 24 |
| coolant | 30000 | 24 |
| spark_plugs | 30000 | 36 |
| air_filter | 15000 | 12 |
| fuel_filter | 30000 | 24 |

**Note:** Intervals can be customized via settings (service_intervals JSON setting)

---

## Frontend Integration

### Maintenance View

- Maintenance list with filter by vehicle
- Add/edit maintenance form with all fields
- Parts used as JSON array input
- Service timeline visualization (Gantt chart)
- Document upload button

### Dashboard View

- Recent maintenance entries
- Service status summary (overdue/upcoming/ok counts)
- Maintenance cost aggregation

---

## Notes

- Service intervals configurable via settings
- Timeline calculation uses dateutil.relativedelta for month arithmetic
- Parts stored as JSON text, serialized/deserialized in route handlers
- Service documents use same upload folder as vehicle photos
- Test mode support via test_key field for data isolation
