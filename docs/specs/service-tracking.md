# Service Tracking Specification

**Related to:** JTBD-001

**Last Updated:** 2026-02-23

---

## Overview

The service tracking system allows users to log and track all maintenance and service activities for their vehicles. It includes interval-based reminders and timeline visualization.

---

## Basic Capability

### Service Entity

**Fields:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `service_date` (date)
- `mileage` (integer, odometer at service time)
- `service_type` (string, e.g., "Oil Change", "Tire Rotation")
- `description` (text, optional, detailed notes)
- `cost` (decimal, optional)
- `odometer_unit` (string, default "miles")
- `created_at` (timestamp)
- `updated_at` (timestamp)

### CRUD Operations

**Create Service:**
- Endpoint: `POST /api/maintenance`
- Required fields: `vehicle_id`, `service_date`, `service_type`
- Optional fields: all others
- Returns: Created service object

**Read Services:**
- List all: `GET /api/maintenance`
- Filter by vehicle: `GET /api/maintenance?vehicle_id=<id>`
- Get one: `GET /api/maintenance/<id>`
- Returns: Service object(s)

**Update Service:**
- Endpoint: `PUT /api/maintenance/<id>`
- Accepts: Any service fields
- Returns: Updated service object

**Delete Service:**
- Endpoint: `DELETE /api/maintenance/<id>`
- Returns: 204 No Content

---

## Enhanced Capability

### Parts Used Tracking

**Field:**
- `parts_used` (text, stored as JSON array)

**Format:**
```json
[
  {"name": "Oil Filter", "part_number": "OF-123", "cost": 12.99},
  {"name": "Engine Oil 5W-30", "part_number": "EO-530", "cost": 35.50}
]
```

**Storage:**
- Stored as JSON text in database
- Serialized/deserialized automatically in API

### Service Intervals

**ServiceInterval Entity:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `service_type` (string)
- `interval_miles` (integer, optional)
- `interval_months` (integer, optional)
- `last_service_date` (date, optional)
- `last_service_mileage` (integer, optional)
- `created_at` (timestamp)

**Create Interval:**
- Endpoint: `POST /api/maintenance/intervals`
- Required: `vehicle_id`, `service_type`
- Optional: `interval_miles`, `interval_months`
- Returns: Created interval object

**Get Intervals:**
- Endpoint: `GET /api/maintenance/intervals?vehicle_id=<id>`
- Returns: Array of interval objects

**Update Interval:**
- Endpoint: `PUT /api/maintenance/intervals/<id>`
- Returns: Updated interval object

**Delete Interval:**
- Endpoint: `DELETE /api/maintenance/intervals/<id>`
- Returns: 204 No Content

### Automatic Reminder Creation

**Behavior:**
- When a service is logged, update the corresponding interval's `last_service_date` and `last_service_mileage`
- Calculate next due date/mileage based on interval
- Create reminder entries (see Reminders section)

**Reminder Entity:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `service_type` (string)
- `due_date` (date, optional)
- `due_mileage` (integer, optional)
- `status` (string: "pending", "completed", "overdue")
- `created_at` (timestamp)

**Get Reminders:**
- Endpoint: `GET /api/maintenance/reminders?vehicle_id=<id>`
- Filter by status: `GET /api/maintenance/reminders?status=overdue`
- Returns: Array of reminder objects

**Complete Reminder:**
- Endpoint: `PUT /api/maintenance/reminders/<id>/complete`
- Behavior: Marks reminder as completed
- Returns: Updated reminder object

---

## Advanced Capability

### Maintenance Timeline

**Timeline Endpoint:**
- Endpoint: `GET /api/maintenance/timeline?vehicle_id=<id>`
- Returns: Array of timeline items with status

**Timeline Item:**
```json
{
  "service_type": "Oil Change",
  "last_service_date": "2024-01-15",
  "last_service_mileage": 42000,
  "next_due_date": "2024-07-15",
  "next_due_mileage": 47000,
  "status": "ok",
  "days_until_due": 45,
  "miles_until_due": 5000
}
```

**Status Values:**
- `ok`: Not due within next 30 days or 1000 miles
- `upcoming`: Due within next 30 days or 1000 miles
- `overdue`: Past due date or mileage

**Timeline Calculation:**
- Use interval settings for each service type
- If no interval exists, use defaults:
  - Oil Change: 5000 miles / 6 months
  - Tire Rotation: 7500 miles / 12 months
  - Brake Service: 30000 miles / 24 months
  - Transmission: 60000 miles / 48 months
  - Coolant: 100000 miles / 60 months

### Service History

**Get Service History:**
- Endpoint: `GET /api/maintenance/history?vehicle_id=<id>`
- Optional filters: `start_date`, `end_date`, `service_type`
- Sort: By date descending (newest first)
- Returns: Array of service records

**Service History with Aggregation:**
- Endpoint: `GET /api/maintenance/history/summary?vehicle_id=<id>`
- Returns:
```json
{
  "total_services": 25,
  "total_cost": 2450.75,
  "services_by_type": {
    "Oil Change": {"count": 12, "total_cost": 780.00},
    "Tire Rotation": {"count": 8, "total_cost": 320.00}
  },
  "first_service_date": "2020-04-01",
  "last_service_date": "2024-06-15"
}
```

---

## Acceptance Criteria

### Basic

- [ ] Create service entry with required fields
- [ ] Update service entry
- [ ] Delete service entry
- [ ] List all services
- [ ] Filter services by vehicle
- [ ] Get single service details
- [ ] Validate required fields
- [ ] Return 404 for non-existent service

### Enhanced

- [ ] Store parts_used as JSON array
- [ ] Retrieve parts_used as parsed JSON
- [ ] Create service intervals
- [ ] Update interval last service date/mileage when service logged
- [ ] Generate reminders from intervals
- [ ] Filter reminders by status
- [ ] Mark reminders as completed
- [ ] Auto-create reminders when service logged

### Advanced

- [ ] Timeline shows all service types with status
- [ ] Status correctly calculated (ok/upcoming/overdue)
- [ ] Timeline respects interval settings
- [ ] Timeline uses defaults when no interval exists
- [ ] Service history sorted by date descending
- [ ] History supports date range filtering
- [ ] History summary aggregates by service type
- [ ] Cascade delete when vehicle deleted

---

## Edge Cases

### Validation

- Service date cannot be in the future
- Mileage cannot be negative
- Cost cannot be negative
- Service type cannot be empty
- Interval miles/months: at least one must be provided

### Timeline Status Logic

```python
def calculate_status(due_date, due_mileage, current_date, current_mileage):
    days_until = (due_date - current_date).days
    miles_until = due_mileage - current_mileage
    
    if days_until < 0 or miles_until < 0:
        return "overdue"
    elif days_until <= 30 or miles_until <= 1000:
        return "upcoming"
    else:
        return "ok"
```

### Cascade Delete

When a vehicle is deleted:
- Delete all service records
- Delete all service intervals
- Delete all reminders

When a service is deleted:
- Do NOT update interval (preserve historical record)

---

## Data Relationships

```
Vehicle (1) ──→ (many) Service
Vehicle (1) ──→ (many) ServiceInterval
Vehicle (1) ──→ (many) Reminder
```

---

## API Response Format

### Service Object

```json
{
  "id": 1,
  "vehicle_id": 1,
  "service_date": "2024-06-15",
  "mileage": 45000,
  "service_type": "Oil Change",
  "description": "Regular maintenance, used synthetic oil",
  "cost": 85.50,
  "parts_used": [
    {"name": "Oil Filter", "part_number": "OF-123", "cost": 12.99},
    {"name": "Engine Oil 5W-30", "part_number": "EO-530", "cost": 35.50}
  ],
  "created_at": "2024-06-15T14:30:00Z",
  "updated_at": "2024-06-15T14:30:00Z"
}
```

### Reminder Object

```json
{
  "id": 1,
  "vehicle_id": 1,
  "service_type": "Oil Change",
  "due_date": "2024-07-15",
  "due_mileage": 47000,
  "status": "upcoming",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Timeline Item

```json
{
  "service_type": "Oil Change",
  "last_service_date": "2024-01-15",
  "last_service_mileage": 42000,
  "next_due_date": "2024-07-15",
  "next_due_mileage": 47000,
  "status": "ok",
  "days_until_due": 45,
  "miles_until_due": 5000
}
```

---

## Notes

- Service types are free-form text (no predefined list)
- Intervals are per-vehicle (different vehicles can have different intervals)
- Reminders are auto-generated, not manually created
- Timeline endpoint is read-only (calculated from intervals and services)
