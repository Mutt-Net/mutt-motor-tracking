# Vehicle Management Specification

**Related to:** JTBD-001

**Last Updated:** 2026-02-23

---

## Overview

The vehicle management system allows users to create, view, update, and delete vehicle profiles. Each vehicle serves as the primary entity to which all other data (services, modifications, costs, etc.) is linked.

---

## Basic Capability

### Core Vehicle Entity

**Fields:**
- `id` (integer, primary key)
- `name` (string, display name e.g., "2020 GTI")
- `make` (string, e.g., "Volkswagen")
- `model` (string, e.g., "GTI")
- `year` (integer)
- `vin` (string, optional, 17 characters)
- `license_plate` (string, optional)
- `color` (string, optional)
- `mileage` (integer, current odometer reading)
- `purchase_date` (date, optional)
- `purchase_price` (decimal, optional)
- `is_active` (boolean, default true)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### CRUD Operations

**Create Vehicle:**
- Endpoint: `POST /api/vehicles`
- Required fields: `make`, `model`, `year`
- Optional fields: all others
- Returns: Created vehicle object with `id`

**Read Vehicles:**
- List all: `GET /api/vehicles`
- Get one: `GET /api/vehicles/<id>`
- Returns: Vehicle object(s) with all fields

**Update Vehicle:**
- Endpoint: `PUT /api/vehicles/<id>`
- Accepts: Any vehicle fields
- Returns: Updated vehicle object

**Delete Vehicle:**
- Endpoint: `DELETE /api/vehicles/<id>`
- Behavior: Cascade delete all related data (services, mods, costs, fuel, documents, notes, faults)
- Returns: 204 No Content

---

## Enhanced Capability

### Photo Management

**Photo Entity:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `filename` (string, stored filename)
- `original_filename` (string, user's original filename)
- `mime_type` (string, e.g., "image/jpeg")
- `file_size` (integer, bytes)
- `is_primary` (boolean, default false)
- `uploaded_at` (timestamp)

**Upload Photo:**
- Endpoint: `POST /api/vehicles/<id>/photos`
- Content-Type: `multipart/form-data`
- Field: `photo` (file)
- Validation: Image files only (jpg, jpeg, png, webp), max 10MB
- Behavior: Setting `is_primary=true` unsets other primary photos
- Returns: Photo object

**Get Photos:**
- Endpoint: `GET /api/vehicles/<id>/photos`
- Returns: Array of photo objects

**Get Primary Photo:**
- Endpoint: `GET /api/vehicles/<id>/photo/primary`
- Returns: Primary photo object or 404 if none

**Set Primary Photo:**
- Endpoint: `PUT /api/vehicles/<id>/photos/<photo_id>/primary`
- Behavior: Sets this photo as primary, unsets others
- Returns: Updated photo object

**Delete Photo:**
- Endpoint: `DELETE /api/vehicles/<id>/photos/<photo_id>`
- Behavior: Deletes file from disk and database record
- Returns: 204 No Content

**Photo Storage:**
- Directory: `uploads/vehicles/<vehicle_id>/`
- Filenames: UUID-based to avoid collisions
- Thumbnails: Generate 400x300 thumbnail on upload

---

## Advanced Capability

### Vehicle Import/Export

**Export Vehicle to JSON:**
- Endpoint: `GET /api/vehicles/<id>/export`
- Includes: Vehicle + all related data (services, mods, costs, fuel, documents, notes, faults, photos metadata)
- Format: JSON
- Returns: JSON object (downloaded as file)

**Export All Vehicles:**
- Endpoint: `GET /api/vehicles/export`
- Includes: All vehicles with their related data
- Format: JSON array
- Returns: JSON object (downloaded as file)

**Import Vehicle from JSON:**
- Endpoint: `POST /api/vehicles/import`
- Content-Type: `multipart/form-data` or `application/json`
- Field: `file` (JSON file) or raw JSON body
- Behavior: Creates new vehicle with all related records
- Returns: Created vehicle object with new IDs

**Export to CSV:**
- Endpoint: `GET /api/vehicles/export/csv`
- Includes: All vehicles (basic info only) as CSV
- Returns: CSV file (downloaded)

---

## Acceptance Criteria

### Basic

- [ ] Create vehicle with make, model, year (required)
- [ ] Update any vehicle field
- [ ] Delete vehicle and all related data (cascade)
- [ ] List all vehicles with basic info
- [ ] Get single vehicle with full details
- [ ] Validate required fields on create
- [ ] Return 404 for non-existent vehicle

### Enhanced

- [ ] Upload vehicle photo via multipart/form-data
- [ ] Retrieve all photos for a vehicle
- [ ] Set primary photo (unsets others automatically)
- [ ] Delete photo (removes file and database record)
- [ ] Validate photo file type and size
- [ ] Generate thumbnails on upload
- [ ] Return 404 for non-existent photo

### Advanced

- [ ] Export single vehicle to JSON with all related data
- [ ] Export all vehicles to JSON
- [ ] Import vehicle from JSON file
- [ ] Import creates all related records with new IDs
- [ ] Export vehicles to CSV format
- [ ] Handle import errors gracefully (invalid JSON, missing fields)

---

## Edge Cases

### Validation

- VIN must be 17 characters if provided
- Year must be between 1900 and current year + 1
- Mileage cannot be negative
- Purchase date cannot be in the future
- Photo file size cannot exceed 10MB
- Photo must be valid image (jpg, jpeg, png, webp)

### Cascade Delete

When a vehicle is deleted, also delete:
- All service records
- All modifications
- All cost entries
- All fuel entries
- All documents
- All notes
- All fault codes
- All photos (files and database records)

### Import Validation

- Reject JSON without required vehicle fields
- Handle duplicate VINs (create anyway, don't check uniqueness)
- Sanitize all string inputs
- Validate date formats
- Validate numeric ranges

---

## Data Relationships

```
Vehicle (1) ──→ (many) Service
Vehicle (1) ──→ (many) Modification
Vehicle (1) ──→ (many) Cost
Vehicle (1) ──→ (many) FuelEntry
Vehicle (1) ──→ (many) Document
Vehicle (1) ──→ (many) Note
Vehicle (1) ──→ (many) FaultCode
Vehicle (1) ──→ (many) VehiclePhoto
```

All relationships use cascade delete.

---

## API Response Format

### Success Response

```json
{
  "id": 1,
  "name": "2020 GTI",
  "make": "Volkswagen",
  "model": "GTI",
  "year": 2020,
  "vin": "WVWZZZ3CZWE386666",
  "license_plate": "ABC123",
  "color": "Deep Black Pearl",
  "mileage": 45000,
  "purchase_date": "2020-03-15",
  "purchase_price": 28000.00,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-06-20T14:22:00Z",
  "photo_primary": "/api/vehicles/1/photo/primary"
}
```

### Error Response

```json
{
  "error": "Vehicle not found"
}
```

### Validation Error Response

```json
{
  "error": "Validation failed",
  "details": {
    "year": "Year must be between 1900 and 2027",
    "vin": "VIN must be exactly 17 characters"
  }
}
```

---

## Notes

- Vehicle `name` is auto-generated as "{year} {make} {model}" if not provided
- Photos are stored on disk, not in database
- Import/export preserves all data relationships
- Test mode: vehicles can be marked as test data for isolation
