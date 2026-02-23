# API Reference

**Backend:** Flask REST API  
**Database:** SQLite with SQLAlchemy ORM  
**Generated:** 2026-02-23

---

## Overview

This document describes all API endpoints in the Mutt Motor Tracking application. The backend provides a comprehensive REST API for vehicle management, service tracking, modification tracking, VCDS diagnostics, cost analysis, and settings management.

**Base URL:** `/api`  
**Content Type:** `application/json` (unless otherwise noted)  
**Authentication:** None (local application)

---

## Table of Contents

1. [Dashboard](#dashboard)
2. [Vehicles](#vehicles)
3. [Maintenance/Service](#maintenanceservice)
4. [Modifications](#modifications)
5. [VCDS Diagnostics](#vcds-diagnostics)
6. [Fuel Tracking](#fuel-tracking)
7. [Costs](#costs)
8. [Documents](#documents)
9. [Notes](#notes)
10. [Guides](#guides)
11. [Settings](#settings)
12. [Analytics](#analytics)
13. [Test Mode](#test-mode)

---

## Dashboard

### Get Dashboard Summary

**Endpoint:** `GET /api/dashboard`

**Description:** Returns aggregated statistics for the dashboard view including vehicle counts, service status, costs, and mod status.

**Query Parameters:**
- `vehicle_id` (optional) - Filter stats to specific vehicle

**Response:**
```json
{
  "total_vehicles": 3,
  "total_service_items": 45,
  "overdue_services": 2,
  "upcoming_services": 5,
  "total_mods": 12,
  "total_costs": 5420.50,
  "total_faults": 3,
  "mods_by_status": {
    "planned": 4,
    "in_progress": 2,
    "completed": 6
  }
}
```

---

## Vehicles

### List All Vehicles

**Endpoint:** `GET /api/vehicles`

**Description:** Returns all vehicles in the system.

**Response:**
```json
[
  {
    "id": 1,
    "name": "2020 GTI",
    "make": "Volkswagen",
    "model": "GTI",
    "year": 2020,
    "vin": "WVWZZZ...",
    "license_plate": "ABC123",
    "color": "Deep Black",
    "mileage": 45000,
    "purchase_date": "2020-03-15",
    "purchase_price": 28000.00,
    "is_active": true,
    "photo_primary": "/uploads/vehicles/1/primary.jpg"
  }
]
```

### Get Single Vehicle

**Endpoint:** `GET /api/vehicles/<int:vehicle_id>`

**Description:** Returns a single vehicle with all related data.

**Response:** Vehicle object with nested relationships (services, mods, fuel entries, etc.)

### Create Vehicle

**Endpoint:** `POST /api/vehicles`

**Request Body:**
```json
{
  "name": "2020 GTI",
  "make": "Volkswagen",
  "model": "GTI",
  "year": 2020,
  "vin": "WVWZZZ...",
  "license_plate": "ABC123",
  "color": "Deep Black",
  "mileage": 45000,
  "purchase_date": "2020-03-15",
  "purchase_price": 28000.00,
  "is_active": true
}
```

**Response:** Created vehicle object

### Update Vehicle

**Endpoint:** `PUT /api/vehicles/<int:vehicle_id>`

**Request Body:** Vehicle fields to update (partial update supported)

**Response:** Updated vehicle object

### Delete Vehicle

**Endpoint:** `DELETE /api/vehicles/<int:vehicle_id>`

**Description:** Deletes vehicle and all related records (cascade delete).

**Response:** `{"message": "Vehicle deleted successfully"}`

### Export Vehicle

**Endpoint:** `GET /api/vehicles/<int:vehicle_id>/export`

**Description:** Exports vehicle with all related data as JSON.

**Response:** JSON object containing vehicle and all related records (services, mods, fuel, costs, documents, notes, VCDS faults)

### Import Vehicle

**Endpoint:** `POST /api/vehicles/import`

**Request Body:** Complete vehicle JSON object (from export)

**Response:** Created vehicle with new ID

### Upload Vehicle Photo

**Endpoint:** `POST /api/vehicles/<int:vehicle_id>/photos`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `photo` - Image file

**Response:**
```json
{
  "id": 1,
  "filename": "photo_001.jpg",
  "path": "/uploads/vehicles/1/photo_001.jpg",
  "is_primary": false,
  "uploaded_at": "2026-02-23T10:30:00Z"
}
```

### Set Primary Vehicle Photo

**Endpoint:** `PUT /api/vehicles/<int:vehicle_id>/photos/<int:photo_id>/primary`

**Description:** Sets a photo as primary (unsets other primary flags).

**Response:** Updated photo object

### Delete Vehicle Photo

**Endpoint:** `DELETE /api/vehicles/<int:vehicle_id>/photos/<int:photo_id>`

**Response:** `{"message": "Photo deleted successfully"}`

---

## Maintenance/Service

### List Service Items

**Endpoint:** `GET /api/maintenance`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (ok, upcoming, overdue, completed)
- `category` (optional) - Filter by category

**Response:** Array of service items with timeline status

### Get Service Item

**Endpoint:** `GET /api/maintenance/<int:service_id>`

**Response:** Service item with full details

### Create Service Item

**Endpoint:** `POST /api/maintenance`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "name": "Oil Change",
  "category": "Engine",
  "status": "ok",
  "due_date": "2026-06-15",
  "due_mileage": 50000,
  "interval_months": 6,
  "interval_miles": 5000,
  "last_performed_date": "2025-12-15",
  "last_performed_mileage": 45000,
  "notes": "Use 5W-30 synthetic",
  "parts_used": ["Oil filter VF123", "5W-30 Oil 5qt"],
  "cost": 75.00
}
```

**Response:** Created service item

### Update Service Item

**Endpoint:** `PUT /api/maintenance/<int:service_id>`

**Request Body:** Service fields to update

**Response:** Updated service item

### Delete Service Item

**Endpoint:** `DELETE /api/maintenance/<int:service_id>`

**Response:** `{"message": "Service item deleted successfully"}`

### Mark Service Complete

**Endpoint:** `POST /api/maintenance/<int:service_id>/complete`

**Request Body:**
```json
{
  "performed_date": "2026-02-23",
  "performed_mileage": 48500,
  "cost": 75.00,
  "parts_used": ["Oil filter VF123", "5W-30 Oil 5qt"],
  "notes": "Completed at dealership"
}
```

**Response:** Updated service item with completed status

### Get Maintenance Timeline

**Endpoint:** `GET /api/maintenance/timeline`

**Query Parameters:**
- `vehicle_id` (required) - Vehicle to get timeline for

**Response:**
```json
{
  "vehicle_id": 1,
  "timeline": [
    {
      "id": 1,
      "name": "Oil Change",
      "status": "overdue",
      "due_date": "2026-02-15",
      "days_overdue": 8,
      "priority": "high"
    },
    {
      "id": 2,
      "name": "Tire Rotation",
      "status": "upcoming",
      "due_date": "2026-03-15",
      "days_until": 20,
      "priority": "medium"
    }
  ],
  "summary": {
    "total": 12,
    "overdue": 2,
    "upcoming": 3,
    "ok": 7
  }
}
```

### Create Service Reminder

**Endpoint:** `POST /api/maintenance/reminders`

**Description:** Auto-creates reminders from service intervals.

**Request Body:**
```json
{
  "vehicle_id": 1,
  "service_template_id": 5
}
```

**Response:** Created reminder service item

---

## Modifications

### List Mods

**Endpoint:** `GET /api/mods`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (planned, in_progress, completed)
- `category` (optional) - Filter by category

**Response:** Array of modification objects

### Get Single Mod

**Endpoint:** `GET /api/mods/<int:mod_id>`

**Response:** Modification with full details

### Create Mod

**Endpoint:** `POST /api/mods`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "name": "Stage 1 ECU Tune",
  "category": "Engine",
  "status": "planned",
  "description": "APR Stage 1 ECU flash",
  "parts": ["APR ECU flash", "Downpipe"],
  "cost_estimate": 650.00,
  "cost_actual": null,
  "started_date": null,
  "completed_date": null,
  "notes": "Requires 93 octane fuel"
}
```

**Response:** Created modification

### Update Mod

**Endpoint:** `PUT /api/mods/<int:mod_id>`

**Request Body:** Modification fields to update

**Response:** Updated modification

### Delete Mod

**Endpoint:** `DELETE /api/mods/<int:mod_id>`

**Response:** `{"message": "Modification deleted successfully"}`

### Update Mod Status

**Endpoint:** `POST /api/mods/<int:mod_id>/status`

**Request Body:**
```json
{
  "status": "in_progress",
  "started_date": "2026-02-23"
}
```

**Response:** Updated modification with new status

---

## VCDS Diagnostics

### List Faults

**Endpoint:** `GET /api/vcds`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (active, cleared)
- `system` (optional) - Filter by system (Engine, Transmission, ABS, etc.)

**Response:** Array of VCDS fault objects

### Get Single Fault

**Endpoint:** `GET /api/vcds/<int:fault_id>`

**Response:** Fault with full details

### Create Fault (Manual Entry)

**Endpoint:** `POST /api/vcds`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "fault_code": "P0300",
  "system": "Engine",
  "description": "Random/Multiple Cylinder Misfire Detected",
  "status": "active",
  "detected_date": "2026-02-20",
  "cleared_date": null,
  "notes": "Intermittent, occurs under load"
}
```

**Response:** Created fault

### Update Fault

**Endpoint:** `PUT /api/vcds/<int:fault_id>`

**Request Body:** Fault fields to update

**Response:** Updated fault

### Delete Fault

**Endpoint:** `DELETE /api/vcds/<int:fault_id>`

**Response:** `{"message": "Fault deleted successfully"}`

### Mark Fault Cleared

**Endpoint:** `POST /api/vcds/<int:fault_id>/clear`

**Request Body:**
```json
{
  "cleared_date": "2026-02-23",
  "notes": "Cleared after replacing spark plugs"
}
```

**Response:** Updated fault with cleared status

### Parse VCDS Text

**Endpoint:** `POST /api/vcds/parse`

**Description:** Parses VCDS log text and extracts fault codes.

**Request Body:**
```json
{
  "text": "VCDS Version: 22.3.0\n\nAddress 01: Engine\n  1 Fault Found:\n  P0300 - Random/Multiple Cylinder Misfire Detected"
}
```

**Response:**
```json
{
  "faults": [
    {
      "fault_code": "P0300",
      "system": "Engine",
      "description": "Random/Multiple Cylinder Misfire Detected"
    }
  ],
  "vcds_version": "22.3.0"
}
```

### Import VCDS Log

**Endpoint:** `POST /api/vcds/import`

**Description:** Parses VCDS text and creates fault records.

**Request Body:**
```json
{
  "vehicle_id": 1,
  "text": "VCDS log content...",
  "scan_date": "2026-02-23"
}
```

**Response:**
```json
{
  "imported_count": 3,
  "faults": [
    { "id": 1, "fault_code": "P0300", ... },
    { "id": 2, "fault_code": "P0420", ... },
    { "id": 3, "fault_code": "C0035", ... }
  ]
}
```

---

## Fuel Tracking

### List Fuel Entries

**Endpoint:** `GET /api/fuel`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `start_date` (optional) - Filter by date range start
- `end_date` (optional) - Filter by date range end

**Response:** Array of fuel entry objects

### Get Fuel Entry

**Endpoint:** `GET /api/fuel/<int:fuel_id>`

**Response:** Fuel entry with full details

### Create Fuel Entry

**Endpoint:** `POST /api/fuel`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "date": "2026-02-23",
  "mileage": 48500,
  "gallons": 12.5,
  "price_per_gallon": 3.45,
  "total_cost": 43.13,
  "station": "Shell",
  "fuel_type": "Premium",
  "is_full_fill": true,
  "notes": "Regular fill-up"
}
```

**Response:** Created fuel entry

### Update Fuel Entry

**Endpoint:** `PUT /api/fuel/<int:fuel_id>`

**Request Body:** Fuel entry fields to update

**Response:** Updated fuel entry

### Delete Fuel Entry

**Endpoint:** `DELETE /api/fuel/<int:fuel_id>`

**Response:** `{"message": "Fuel entry deleted successfully"}`

### Get Fuel Economy

**Endpoint:** `GET /api/fuel/economy`

**Query Parameters:**
- `vehicle_id` (required) - Vehicle to calculate for

**Response:**
```json
{
  "vehicle_id": 1,
  "average_mpg": 28.5,
  "entries_count": 24,
  "total_gallons": 450.5,
  "total_cost": 1554.23,
  "last_calculation": "2026-02-23"
}
```

---

## Costs

### List Costs

**Endpoint:** `GET /api/costs`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `category` (optional) - Filter by category (service, mod, fuel, other)
- `start_date` (optional) - Date range start
- `end_date` (optional) - Date range end

**Response:** Array of cost objects

### Get Cost Summary

**Endpoint:** `GET /api/costs/summary`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `start_date` (optional) - Date range start
- `end_date` (optional) - Date range end
- `group_by` (optional) - Group by (category, month, year)

**Response:**
```json
{
  "total": 5420.50,
  "by_category": {
    "service": 1250.00,
    "mod": 3500.00,
    "fuel": 670.50
  },
  "by_month": {
    "2026-01": 450.00,
    "2026-02": 320.50
  }
}
```

### Create Cost Entry

**Endpoint:** `POST /api/costs`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "category": "service",
  "amount": 75.00,
  "date": "2026-02-23",
  "description": "Oil change",
  "payment_method": "Credit Card",
  "receipt_url": "/uploads/receipts/001.pdf",
  "notes": "Dealership service"
}
```

**Response:** Created cost entry

### Update Cost Entry

**Endpoint:** `PUT /api/costs/<int:cost_id>`

**Request Body:** Cost fields to update

**Response:** Updated cost entry

### Delete Cost Entry

**Endpoint:** `DELETE /api/costs/<int:cost_id>`

**Response:** `{"message": "Cost entry deleted successfully"}`

---

## Documents

### List Documents

**Endpoint:** `GET /api/documents`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `type` (optional) - Filter by type (receipt, manual, warranty, other)

**Response:** Array of document objects

### Get Document

**Endpoint:** `GET /api/documents/<int:document_id>`

**Response:** Document with full details

### Upload Document

**Endpoint:** `POST /api/documents`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` - Document file
- `vehicle_id` - Associated vehicle
- `type` - Document type (receipt, manual, warranty, other)
- `description` - Optional description

**Response:**
```json
{
  "id": 1,
  "filename": "receipt_001.pdf",
  "path": "/uploads/documents/1/receipt_001.pdf",
  "type": "receipt",
  "vehicle_id": 1,
  "uploaded_at": "2026-02-23T10:30:00Z"
}
```

### Delete Document

**Endpoint:** `DELETE /api/documents/<int:document_id>`

**Response:** `{"message": "Document deleted successfully"}`

### Get File

**Endpoint:** `GET /api/files/<path:filename>`

**Description:** Serves uploaded files (documents, receipts, photos).

**Response:** File content with appropriate Content-Type

---

## Notes

### List Notes

**Endpoint:** `GET /api/notes`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `entity_type` (optional) - Filter by entity type (vehicle, service, mod, etc.)
- `entity_id` (optional) - Filter by entity ID

**Response:** Array of note objects

### Get Note

**Endpoint:** `GET /api/notes/<int:note_id>`

**Response:** Note with full details

### Create Note

**Endpoint:** `POST /api/notes`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "entity_type": "service",
  "entity_id": 5,
  "content": "Remember to use OEM filter next time",
  "tags": ["reminder", "service"]
}
```

**Response:** Created note

### Update Note

**Endpoint:** `PUT /api/notes/<int:note_id>`

**Request Body:** Note fields to update

**Response:** Updated note

### Delete Note

**Endpoint:** `DELETE /api/notes/<int:note_id>`

**Response:** `{"message": "Note deleted successfully"}`

---

## Guides

### List Guides

**Endpoint:** `GET /api/guides`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `category` (optional) - Filter by category

**Response:** Array of guide objects

### Get Guide

**Endpoint:** `GET /api/guides/<int:guide_id>`

**Response:** Guide with full details including intervals

### Create Guide

**Endpoint:** `POST /api/guides`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "title": "Oil Change Guide",
  "category": "Maintenance",
  "content": "Step-by-step instructions...",
  "interval_miles": 5000,
  "interval_months": 6,
  "is_template": false
}
```

**Response:** Created guide

### Update Guide

**Endpoint:** `PUT /api/guides/<int:guide_id>`

**Request Body:** Guide fields to update

**Response:** Updated guide

### Delete Guide

**Endpoint:** `DELETE /api/guides/<int:guide_id>`

**Response:** `{"message": "Guide deleted successfully"}`

### Load Guide Templates

**Endpoint:** `POST /api/guides/templates`

**Description:** Loads predefined guide templates into the database.

**Request Body:** (optional)
```json
{
  "vehicle_id": 1
}
```

**Response:**
```json
{
  "loaded_count": 12,
  "templates": ["Oil Change", "Tire Rotation", "Brake Service", ...]
}
```

---

## Settings

### Get Settings

**Endpoint:** `GET /api/settings`

**Description:** Returns all application settings.

**Response:**
```json
{
  "currency_symbol": "$",
  "distance_unit": "miles",
  "temperature_unit": "F",
  "total_spend_include_service": true,
  "total_spend_include_mods": true,
  "total_spend_include_fuel": false,
  "test_mode": false,
  "default_vehicle_id": 1
}
```

### Update Settings

**Endpoint:** `PUT /api/settings`

**Request Body:** Settings fields to update (partial update supported)

**Response:** Updated settings

### Export Settings

**Endpoint:** `GET /api/settings/export`

**Description:** Exports settings as JSON backup file.

**Response:** JSON settings object

### Import Settings

**Endpoint:** `POST /api/settings/import`

**Request Body:** Settings JSON object

**Response:** `{"message": "Settings imported successfully"}`

### Export All Data (CSV)

**Endpoint:** `GET /api/settings/export/csv`

**Description:** Exports all data as CSV files (one per table).

**Response:** ZIP file containing CSV exports

---

## Analytics

### Get Analytics Data

**Endpoint:** `GET /api/analytics`

**Query Parameters:**
- `vehicle_id` (required) - Vehicle to analyze
- `metric` (optional) - Specific metric (costs, fuel, service)
- `period` (optional) - Time period (month, year, all)

**Response:**
```json
{
  "vehicle_id": 1,
  "costs": {
    "total": 5420.50,
    "by_month": [...],
    "by_category": {...}
  },
  "fuel": {
    "average_mpg": 28.5,
    "entries": [...],
    "trend": [...]
  },
  "service": {
    "total_services": 12,
    "completed": 10,
    "upcoming": 2,
    "overdue": 0
  }
}
```

### Get Cost Trends

**Endpoint:** `GET /api/analytics/costs`

**Query Parameters:**
- `vehicle_id` (required)
- `group_by` (optional) - month, quarter, year

**Response:** Time series data for cost analysis

### Get Fuel Trends

**Endpoint:** `GET /api/analytics/fuel`

**Query Parameters:**
- `vehicle_id` (required)

**Response:** MPG trend over time

---

## Test Mode

### Enable Test Mode

**Endpoint:** `POST /api/test/enable`

**Description:** Enables test mode for data isolation.

**Response:** `{"message": "Test mode enabled", "test_mode": true}`

### Disable Test Mode

**Endpoint:** `POST /api/test/disable`

**Response:** `{"message": "Test mode disabled", "test_mode": false}`

### Clear Test Data

**Endpoint:** `DELETE /api/test/clear`

**Description:** Deletes all test data (marked with test flag).

**Response:** `{"message": "Test data cleared", "deleted_count": 15}`

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented (local application).

---

## File Uploads

**Upload Directory:** `uploads/` (relative to backend root)

**Subdirectories:**
- `uploads/vehicles/<vehicle_id>/` - Vehicle photos
- `uploads/documents/<document_id>/` - General documents
- `uploads/receipts/` - Receipt files

**Supported File Types:**
- Images: JPG, PNG, GIF, WEBP
- Documents: PDF, TXT, MD

**Max File Size:** 10MB (configurable)

---

## Database Models

The API is backed by 12 SQLAlchemy models:

1. **Vehicle** - Vehicle information
2. **Service** - Maintenance/service records
3. **Modification** - Vehicle modifications
4. **VCDSFault** - Diagnostic fault codes
5. **FuelEntry** - Fuel fill-up records
6. **Cost** - Cost tracking
7. **Document** - Document/receipt metadata
8. **Note** - User notes
9. **Guide** - How-to guides
10. **Settings** - Application settings
11. **VehiclePhoto** - Vehicle photo metadata
12. **TestFlag** - Test data isolation marker

---

## Notes

- All dates are in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- All monetary values are in the configured currency (default: USD)
- All distances are in configured units (default: miles)
- Cascade delete is implemented for all vehicle relationships
- Test mode filters data using the TestFlag model
