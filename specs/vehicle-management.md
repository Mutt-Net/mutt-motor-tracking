# Vehicle Management Specification

**Related to:** JTBD-001 (Service record tracking)

**Description:** Create, view, update, and delete vehicle profiles with detailed specifications. Support multiple vehicles with photo management and data export/import capabilities.

---

## Capability Depths

### Basic

Minimal viable implementation for vehicle profiles:

- Single vehicle support with core fields:
  - Name, VIN, registration
  - Year, make, model
  - Engine, transmission
  - Current mileage
- CRUD operations via REST API
- List all vehicles with summary data

### Enhanced

Additional features for vehicle management:

- Multiple vehicle support
- Vehicle photo management:
  - Upload photos (PNG, JPG, JPEG, GIF, WebP, BMP)
  - Set primary photo per vehicle
  - Caption support
  - Automatic primary photo unsetting when changed
- Vehicle dashboard with aggregated statistics

### Advanced

Edge cases and integrations:

- Export vehicle data to JSON format
- Import vehicle data from JSON (with related records)
- CSV export of all vehicle data
- Cascade delete removes all related records (maintenance, mods, costs, etc.)

---

## Data Model

### Vehicle Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| name | String(100) | Not Null | Vehicle nickname/display name |
| reg | String(20) | Unique | Registration/license plate |
| vin | String(17) | Unique | Vehicle Identification Number |
| year | Integer | | Manufacturing year |
| make | String(50) | | Manufacturer (e.g., "Volkswagen") |
| model | String(50) | | Model name (e.g., "EOS") |
| engine | String(100) | | Engine specification |
| transmission | String(50) | | Transmission type |
| mileage | Integer | Default: 0 | Current odometer reading |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

### VehiclePhoto Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| filename | String(200) | | Stored filename (UUID) |
| caption | String(500) | | Photo description |
| is_primary | Boolean | Default: False | Primary photo flag |
| created_at | DateTime | Default: UTC now | Upload timestamp |

---

## API Endpoints

### Vehicle CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vehicles | List all vehicles |
| POST | /api/vehicles | Create new vehicle |
| GET | /api/vehicles/{id} | Get vehicle by ID |
| PUT | /api/vehicles/{id} | Update vehicle |
| DELETE | /api/vehicles/{id} | Delete vehicle (cascade) |
| POST | /api/vehicles/import | Import vehicle from JSON |

### Vehicle Photos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vehicle-photos?vehicle_id= | Get photos for vehicle |
| POST | /api/vehicle-photos | Add photo to vehicle |
| PUT | /api/vehicle-photos/{id} | Update photo metadata |
| DELETE | /api/vehicle-photos/{id} | Delete photo |

### Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard | Get aggregated stats for all vehicles |
| GET | /api/dashboard/{vehicle_id} | Get stats for specific vehicle |

---

## Acceptance Criteria

### Core Functionality

- [ ] Can create vehicle with full specifications (year, make, model, engine, transmission, mileage, VIN, reg)
- [ ] Can retrieve vehicle by ID with all fields
- [ ] Can update vehicle information
- [ ] Can delete vehicle with cascade delete removing all related records (maintenance, mods, costs, notes, vcds_faults, guides, photos, fuel_entries, reminders, receipts)
- [ ] Can list all vehicles with summary data

### Photo Management

- [ ] Can upload vehicle photos with filename and caption
- [ ] Can set primary photo for a vehicle
- [ ] Setting a photo as primary automatically unsets other primary flags for same vehicle
- [ ] Can retrieve all photos for a vehicle
- [ ] Can delete vehicle photos
- [ ] Photos stored in uploads/ directory with UUID filenames

### Dashboard & Statistics

- [ ] Dashboard returns correct aggregated data per vehicle:
  - Total maintenance cost
  - Total mod cost
  - Total fuel cost
  - Total cost (sum of all categories based on settings)
  - Service timeline status
- [ ] Dashboard respects settings for what's included in total spend
- [ ] Dashboard returns data for all vehicles when no vehicle_id specified

### Data Export/Import

- [ ] Can export vehicle data to JSON format
- [ ] Can import vehicle from JSON with related records
- [ ] CSV export includes all vehicle tables
- [ ] Import validates required fields before creating records

### Validation & Error Handling

- [ ] Vehicle creation validates required fields
- [ ] Duplicate VIN or registration returns error
- [ ] Invalid vehicle ID returns 404
- [ ] All error responses return {'error': 'message'} format
- [ ] Cascade delete verified: deleting vehicle removes records from all 12 related tables

---

## Relationships

### One-to-Many (Vehicle -> Related)

| Related Table | Cascade Behavior |
|---------------|------------------|
| maintenance | DELETE CASCADE |
| mods | DELETE CASCADE |
| costs | DELETE CASCADE |
| notes | DELETE CASCADE |
| vcds_faults | DELETE CASCADE |
| guides | DELETE CASCADE |
| vehicle_photos | DELETE CASCADE |
| fuel_entries | DELETE CASCADE |
| reminders | DELETE CASCADE |
| receipts | DELETE CASCADE |
| service_documents | DELETE CASCADE |

---

## Frontend Integration

### Vehicle View

- Vehicle list with search/filter
- Vehicle detail form with all fields
- Photo gallery with primary indicator
- Delete confirmation with cascade warning

### Dashboard View

- Summary cards showing:
  - Total vehicles
  - Total spend (all vehicles)
  - Average cost per vehicle
  - Service status overview
- Chart.js integration for cost breakdown

---

## Notes

- Default vehicle (VW EOS) created on first run via backend/app.py
- Photos stored in uploads/ directory at project root
- File upload supports: PNG, JPG, JPEG, GIF, WebP, BMP, PDF
- UUID used for filename security
- Test mode support via test_key field for data isolation
