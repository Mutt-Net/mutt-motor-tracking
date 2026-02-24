# API Reference

**Backend:** Flask REST API
**Database:** SQLite with SQLAlchemy ORM
**Generated:** 2026-02-23
**Last Updated:** 2026-02-23

---

## Overview

This document describes all API endpoints in the Mutt Motor Tracking application. The backend provides a comprehensive REST API for vehicle management, service tracking, modification tracking, VCDS diagnostics, cost analysis, fuel tracking, and documentation.

**Base URL:** `/api`
**Content Type:** `application/json` (unless otherwise noted)
**Authentication:** None (local application)

**Total Endpoints:** 52

---

## Table of Contents

1. [Health Check](#health-check)
2. [Dashboard](#dashboard)
3. [Vehicles](#vehicles)
4. [Vehicle Photos](#vehicle-photos)
5. [Maintenance/Service](#maintenanceservice)
6. [Service Intervals](#service-intervals)
7. [Reminders](#reminders)
8. [Maintenance Timeline](#maintenance-timeline)
9. [Modifications](#modifications)
10. [VCDS Diagnostics](#vcds-diagnostics)
11. [Costs](#costs)
12. [Analytics](#analytics)
13. [Fuel Tracking](#fuel-tracking)
14. [Documents](#documents)
15. [File Upload](#file-upload)
16. [Notes](#notes)
17. [Settings](#settings)
18. [Guides](#guides)

---

## Health Check

### Health Check

**Endpoint:** `GET /api/health`

**Description:** Returns API health status.

**Response:**
```json
{
  "status": "ok",
  "message": "Mutt Motor Tracking API"
}
```

---

## Dashboard

### Get Dashboard Summary

**Endpoint:** `GET /api/dashboard`

**Description:** Returns aggregated statistics for the dashboard view including vehicle counts, service status, costs, and fault codes.

**Response:**
```json
{
  "total_vehicles": 3,
  "total_services": 45,
  "total_modifications": 12,
  "total_active_faults": 3,
  "total_cost": 5420.50,
  "total_mod_cost": 2500.00,
  "upcoming_reminders": 5,
  "overdue_services": 2
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
    "is_active": true
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

**Validation:** `name`, `make`, and `model` are required.

**Response:** Created vehicle object (201)

### Update Vehicle

**Endpoint:** `PUT /api/vehicles/<int:vehicle_id>`

**Request Body:** Vehicle fields to update (partial update supported)

**Response:** Updated vehicle object

### Delete Vehicle

**Endpoint:** `DELETE /api/vehicles/<int:vehicle_id>`

**Description:** Deletes vehicle and all related records (cascade delete).

**Response:** `{"message": "Vehicle deleted successfully"}`

### Export Vehicles

**Endpoint:** `GET /api/vehicles/export`

**Description:** Exports all vehicles as JSON.

**Response:**
```json
{
  "exported_at": "2026-02-23T10:30:00Z",
  "vehicles": [...]
}
```

### Import Vehicles

**Endpoint:** `POST /api/vehicles/import`

**Request Body:**
```json
{
  "vehicles": [
    {
      "name": "2020 GTI",
      "make": "Volkswagen",
      "model": "GTI",
      ...
    }
  ]
}
```

**Response:**
```json
{
  "message": "Imported 2 vehicles",
  "vehicles": ["2020 GTI", "2018 Golf R"]
}
```

---

## Vehicle Photos

### List Vehicle Photos

**Endpoint:** `GET /api/vehicles/<int:vehicle_id>/photos`

**Description:** Returns all photos for a specific vehicle.

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "filename": "1_1708689000.123456_photo.jpg",
    "original_filename": "photo.jpg",
    "is_primary": true,
    "uploaded_at": "2026-02-23T10:30:00Z"
  }
]
```

### Upload Vehicle Photo

**Endpoint:** `POST /api/vehicles/<int:vehicle_id>/photos`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` - Image file (JPG, PNG, GIF, WEBP)

**Response:**
```json
{
  "id": 1,
  "vehicle_id": 1,
  "filename": "1_1708689000.123456_photo.jpg",
  "original_filename": "photo.jpg",
  "is_primary": false,
  "uploaded_at": "2026-02-23T10:30:00Z"
}
```

### Delete Vehicle Photo

**Endpoint:** `DELETE /api/photos/<int:photo_id>`

**Description:** Deletes a photo and removes the file from disk.

**Response:** `{"message": "Photo deleted successfully"}`

### Set Primary Vehicle Photo

**Endpoint:** `POST /api/photos/<int:photo_id>/primary`

**Description:** Sets a photo as primary (unsets other primary flags for the vehicle).

**Response:** Updated photo object

---

## Maintenance/Service

### List All Services

**Endpoint:** `GET /api/maintenance`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "service_date": "2026-02-15",
    "mileage": 45000,
    "description": "Oil change",
    "cost": 75.00,
    "parts_used": ["Oil filter VF123", "5W-30 Oil 5qt"],
    "service_type": "Oil Change",
    "notes": "Dealership service"
  }
]
```

### Get Single Service

**Endpoint:** `GET /api/maintenance/<int:service_id>`

**Response:** Service item with full details

### Create Service

**Endpoint:** `POST /api/maintenance`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "service_date": "2026-02-15",
  "mileage": 45000,
  "description": "Oil change",
  "cost": 75.00,
  "parts_used": ["Oil filter VF123", "5W-30 Oil 5qt"],
  "service_type": "Oil Change",
  "notes": "Dealership service"
}
```

**Validation:** `vehicle_id` and `service_date` are required.

**Response:** Created service item (201)

### Update Service

**Endpoint:** `PUT /api/maintenance/<int:service_id>`

**Request Body:** Service fields to update (partial update supported)

**Response:** Updated service item

### Delete Service

**Endpoint:** `DELETE /api/maintenance/<int:service_id>`

**Response:** `{"message": "Service deleted successfully"}`

---

## Service Intervals

### List Service Intervals

**Endpoint:** `GET /api/maintenance/intervals`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "name": "Oil Change",
    "interval_miles": 5000,
    "interval_months": 6,
    "last_service_date": "2026-02-15",
    "last_service_mileage": 45000,
    "is_active": true
  }
]
```

### Create Service Interval

**Endpoint:** `POST /api/maintenance/intervals`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "name": "Oil Change",
  "interval_miles": 5000,
  "interval_months": 6,
  "last_service_date": "2026-02-15",
  "last_service_mileage": 45000,
  "is_active": true
}
```

**Validation:** `vehicle_id` and `name` are required.

**Response:** Created service interval (201)

### Delete Service Interval

**Endpoint:** `DELETE /api/maintenance/intervals/<int:interval_id>`

**Response:** `{"message": "Interval deleted successfully"}`

---

## Reminders

### List Reminders

**Endpoint:** `GET /api/maintenance/reminders`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (pending, completed)

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "name": "Oil Change Due",
    "due_date": "2026-08-15",
    "status": "pending",
    "notes": "6 months since last oil change"
  }
]
```

### Update Reminder

**Endpoint:** `PUT /api/maintenance/reminders/<int:reminder_id>`

**Request Body:**
```json
{
  "status": "completed",
  "completed_date": "2026-02-23",
  "notes": "Completed early"
}
```

**Response:** Updated reminder

### Complete Reminder

**Endpoint:** `POST /api/maintenance/reminders/<int:reminder_id>/complete`

**Description:** Marks a reminder as completed with current date.

**Response:** Updated reminder with status "completed"

---

## Maintenance Timeline

### Get Maintenance Timeline

**Endpoint:** `GET /api/maintenance/timeline`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "interval_id": 1,
    "vehicle_id": 1,
    "name": "Oil Change",
    "last_service_date": "2026-02-15",
    "last_service_mileage": 45000,
    "next_due_date": "2026-08-15",
    "next_due_mileage": 50000,
    "status": "ok",
    "interval_months": 6,
    "interval_miles": 5000
  }
]
```

**Status Values:**
- `ok` - Service is current
- `upcoming` - Due within 30 days
- `overdue` - Past due date

---

## Modifications

### List All Modifications

**Endpoint:** `GET /api/mods`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (planned, in_progress, completed)

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "name": "Stage 1 ECU Tune",
    "description": "APR ECU flash",
    "status": "planned",
    "cost": 650.00,
    "parts": ["APR ECU flash", "Downpipe"],
    "installation_notes": "Requires 93 octane fuel",
    "vendor": "APR",
    "vendor_link": "https://example.com",
    "created_at": "2026-02-01T10:00:00Z"
  }
]
```

### Get Single Modification

**Endpoint:** `GET /api/mods/<int:mod_id>`

**Response:** Modification with full details

### Create Modification

**Endpoint:** `POST /api/mods`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "name": "Stage 1 ECU Tune",
  "description": "APR ECU flash",
  "status": "planned",
  "cost": 650.00,
  "parts": ["APR ECU flash", "Downpipe"],
  "installation_notes": "Requires 93 octane fuel",
  "vendor": "APR",
  "vendor_link": "https://example.com"
}
```

**Validation:** `vehicle_id` and `name` are required.

**Response:** Created modification (201)

### Update Modification

**Endpoint:** `PUT /api/mods/<int:mod_id>`

**Request Body:** Modification fields to update (partial update supported)

**Response:** Updated modification

### Delete Modification

**Endpoint:** `DELETE /api/mods/<int:mod_id>`

**Response:** `{"message": "Modification deleted successfully"}`

### Update Modification Status

**Endpoint:** `PUT /api/mods/<int:mod_id>/status`

**Request Body:**
```json
{
  "status": "in_progress"
}
```

**Valid Statuses:** `planned`, `in_progress`, `completed`

**Response:** Updated modification with new status

---

## VCDS Diagnostics

### List All Fault Codes

**Endpoint:** `GET /api/vcds`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `status` (optional) - Filter by status (active, cleared)

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "code": "P0300",
    "description": "Random/Multiple Cylinder Misfire Detected",
    "status": "active",
    "detected_date": "2026-02-20T10:00:00Z",
    "cleared_date": null,
    "notes": "Intermittent, occurs under load"
  }
]
```

### Get Single Fault Code

**Endpoint:** `GET /api/vcds/<int:fault_id>`

**Response:** Fault code with full details

### Create Fault Code

**Endpoint:** `POST /api/vcds`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "code": "P0300",
  "description": "Random/Multiple Cylinder Misfire Detected",
  "status": "active",
  "notes": "Intermittent, occurs under load"
}
```

**Validation:** `vehicle_id` and `code` are required.

**Response:** Created fault code (201)

### Update Fault Code

**Endpoint:** `PUT /api/vcds/<int:fault_id>`

**Request Body:** Fault code fields to update (partial update supported)

**Response:** Updated fault code

### Delete Fault Code

**Endpoint:** `DELETE /api/vcds/<int:fault_id>`

**Response:** `{"message": "Fault code deleted successfully"}`

### Clear Fault Code

**Endpoint:** `POST /api/vcds/<int:fault_id>/clear`

**Description:** Marks a fault as cleared with current timestamp.

**Response:** Updated fault code with status "cleared"

### Activate Fault Code

**Endpoint:** `POST /api/vcds/<int:fault_id>/activate`

**Description:** Marks a fault as active (clears cleared_date).

**Response:** Updated fault code with status "active"

### Parse VCDS Text

**Endpoint:** `POST /api/vcds/parse`

**Description:** Parses VCDS diagnostic text output and extracts fault codes.

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
      "code": "P0300",
      "description": "Random/Multiple Cylinder Misfire Detected",
      "status": "active"
    }
  ],
  "count": 1
}
```

### Import VCDS Faults

**Endpoint:** `POST /api/vcds/import`

**Description:** Imports parsed VCDS faults into the database.

**Request Body:**
```json
{
  "vehicle_id": 1,
  "faults": [
    {
      "code": "P0300",
      "description": "Random/Multiple Cylinder Misfire Detected",
      "status": "active"
    }
  ],
  "skip_existing": true
}
```

**Response:**
```json
{
  "message": "Imported 2 faults, skipped 1",
  "imported": ["P0300", "P0420"],
  "skipped": ["C0035"]
}
```

---

## Costs

### List All Costs

**Endpoint:** `GET /api/costs`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `category` (optional) - Filter by category
- `start_date` (optional) - Filter by date range start
- `end_date` (optional) - Filter by date range end

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "amount": 75.00,
    "category": "service",
    "date": "2026-02-15",
    "description": "Oil change",
    "vendor": "Dealership",
    "notes": "Regular maintenance"
  }
]
```

### Get Single Cost

**Endpoint:** `GET /api/costs/<int:cost_id>`

**Response:** Cost entry with full details

### Create Cost Entry

**Endpoint:** `POST /api/costs`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "amount": 75.00,
  "category": "service",
  "date": "2026-02-15",
  "description": "Oil change",
  "vendor": "Dealership",
  "notes": "Regular maintenance"
}
```

**Validation:** `vehicle_id` and `amount` are required.

**Response:** Created cost entry (201)

### Update Cost Entry

**Endpoint:** `PUT /api/costs/<int:cost_id>`

**Request Body:** Cost fields to update (partial update supported)

**Response:** Updated cost entry

### Delete Cost Entry

**Endpoint:** `DELETE /api/costs/<int:cost_id>`

**Response:** `{"message": "Cost entry deleted successfully"}`

### Get Cost Summary

**Endpoint:** `GET /api/costs/summary`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `category` (optional) - Filter by category
- `start_date` (optional) - Date range start
- `end_date` (optional) - Date range end

**Response:**
```json
{
  "total": 5420.50,
  "by_category": {
    "service": 1250.00,
    "mod": 3500.00,
    "fuel": 670.50
  },
  "count": 24,
  "date_range": {
    "start": null,
    "end": null
  }
}
```

---

## Analytics

### Get Spending Analytics

**Endpoint:** `GET /api/analytics/spending`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `months` (optional, default: 12) - Number of months to include

**Response:**
```json
{
  "by_category": {
    "service": 1250.00,
    "mod": 3500.00,
    "fuel": 670.50
  },
  "by_month": {
    "2026-01": 450.00,
    "2026-02": 320.50
  },
  "total": 5420.50,
  "period_months": 12
}
```

---

## Documents

### List All Documents

**Endpoint:** `GET /api/documents`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "title": "Oil Change Receipt",
    "document_type": "receipt",
    "filename": "receipt_001.pdf",
    "file_path": "/uploads/receipts/receipt_001.pdf",
    "notes": "Dealership service"
  }
]
```

### Get Single Document

**Endpoint:** `GET /api/documents/<int:doc_id>`

**Response:** Document with full details

### Create Document

**Endpoint:** `POST /api/documents`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "title": "Oil Change Receipt",
  "document_type": "receipt",
  "filename": "receipt_001.pdf",
  "file_path": "/uploads/receipts/receipt_001.pdf",
  "notes": "Dealership service"
}
```

**Validation:** `vehicle_id` and `title` are required.

**Response:** Created document (201)

### Update Document

**Endpoint:** `PUT /api/documents/<int:doc_id>`

**Request Body:** Document fields to update (partial update supported)

**Response:** Updated document

### Delete Document

**Endpoint:** `DELETE /api/documents/<int:doc_id>`

**Response:** `{"message": "Document deleted successfully"}`

---

## File Upload

### Upload File

**Endpoint:** `POST /api/upload`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` - Document/receipt file (JPG, PNG, GIF, WEBP, PDF, TXT, MD)

**Response:**
```json
{
  "filename": "1708689000.123456_receipt.pdf",
  "original_filename": "receipt.pdf",
  "file_path": "/uploads/1708689000.123456_receipt.pdf"
}
```

**Supported File Types:** Images (JPG, PNG, GIF, WEBP), Documents (PDF, TXT, MD)

---

## Notes

### List All Notes

**Endpoint:** `GET /api/notes`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "title": "Service Reminder",
    "content": "Remember to use OEM filter next time",
    "created_at": "2026-02-01T10:00:00Z"
  }
]
```

### Get Single Note

**Endpoint:** `GET /api/notes/<int:note_id>`

**Response:** Note with full details

### Create Note

**Endpoint:** `POST /api/notes`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "title": "Service Reminder",
  "content": "Remember to use OEM filter next time"
}
```

**Validation:** `vehicle_id` and `title` are required.

**Response:** Created note (201)

### Update Note

**Endpoint:** `PUT /api/notes/<int:note_id>`

**Request Body:** Note fields to update (partial update supported)

**Response:** Updated note

### Delete Note

**Endpoint:** `DELETE /api/notes/<int:note_id>`

**Response:** `{"message": "Note deleted successfully"}`

---

## Guides

### List All Guides

**Endpoint:** `GET /api/guides`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle
- `is_template` (optional, type: bool) - Filter by template status

**Response:**
```json
[
  {
    "id": 1,
    "title": "Oil Change",
    "description": "Regular oil and filter change",
    "interval_miles": 5000,
    "interval_months": 6,
    "steps": ["Drain old oil", "Replace oil filter", "Add new oil", "Check for leaks"],
    "is_template": true,
    "vehicle_id": null
  }
]
```

### Get Single Guide

**Endpoint:** `GET /api/guides/<int:guide_id>`

**Response:** Guide with full details

### Create Guide

**Endpoint:** `POST /api/guides`

**Request Body:**
```json
{
  "title": "Oil Change",
  "description": "Regular oil and filter change",
  "interval_miles": 5000,
  "interval_months": 6,
  "steps": ["Drain old oil", "Replace oil filter", "Add new oil", "Check for leaks"],
  "is_template": true,
  "vehicle_id": null
}
```

**Validation:** `title` is required.

**Response:** Created guide (201)

### Update Guide

**Endpoint:** `PUT /api/guides/<int:guide_id>`

**Request Body:** Guide fields to update (partial update supported)

**Response:** Updated guide

### Delete Guide

**Endpoint:** `DELETE /api/guides/<int:guide_id>`

**Response:** `{"message": "Guide deleted successfully"}`

### Load Guide Templates

**Endpoint:** `POST /api/guides/templates`

**Description:** Loads default guide templates (Oil Change, Tire Rotation, Brake Inspection) into the database.

**Response:**
```json
{
  "message": "Loaded 3 templates",
  "templates": ["Oil Change", "Tire Rotation", "Brake Inspection"]
}
```

---

## Settings

### Get All Settings

**Endpoint:** `GET /api/settings`

**Response:**
```json
{
  "currency_symbol": {
    "value": "$",
    "description": "Currency symbol for display"
  },
  "distance_unit": {
    "value": "miles",
    "description": "Distance unit (miles or km)"
  },
  "test_mode": {
    "value": "false",
    "description": "Enable test mode for data isolation"
  }
}
```

### Get Single Setting

**Endpoint:** `GET /api/settings/<key>`

**Response:**
```json
{
  "key": "currency_symbol",
  "value": "$",
  "description": "Currency symbol for display"
}
```

### Create or Update Setting

**Endpoint:** `POST /api/settings`

**Request Body:**
```json
{
  "key": "currency_symbol",
  "value": "$",
  "description": "Currency symbol for display"
}
```

**Validation:** `key` and `value` are required.

**Response:** Updated setting

### Backup Settings

**Endpoint:** `GET /api/settings/backup`

**Description:** Exports all settings as JSON backup.

**Response:**
```json
{
  "backed_up_at": "2026-02-23T10:30:00Z",
  "settings": {
    "currency_symbol": {"value": "$", "description": "..."},
    ...
  }
}
```

### Restore Settings

**Endpoint:** `POST /api/settings/restore`

**Request Body:** Settings JSON object (from backup)

**Response:**
```json
{
  "message": "Restored 5 settings",
  "restored": ["currency_symbol", "distance_unit", ...]
}
```

---

## Fuel Tracking

### List All Fuel Entries

**Endpoint:** `GET /api/fuel`

**Query Parameters:**
- `vehicle_id` (optional) - Filter by vehicle

**Response:**
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "date": "2026-02-15",
    "mileage": 45000,
    "gallons": 12.5,
    "price_per_gallon": 3.45,
    "total_cost": 43.13,
    "station": "Shell",
    "is_full_tank": true,
    "notes": "Regular fill-up"
  }
]
```

### Get Single Fuel Entry

**Endpoint:** `GET /api/fuel/<int:entry_id>`

**Response:** Fuel entry with full details

### Create Fuel Entry

**Endpoint:** `POST /api/fuel`

**Request Body:**
```json
{
  "vehicle_id": 1,
  "date": "2026-02-15",
  "mileage": 45000,
  "gallons": 12.5,
  "price_per_gallon": 3.45,
  "total_cost": 43.13,
  "station": "Shell",
  "is_full_tank": true,
  "notes": "Regular fill-up"
}
```

**Validation:** `vehicle_id` and `date` are required.

**Response:** Created fuel entry (201)

### Update Fuel Entry

**Endpoint:** `PUT /api/fuel/<int:entry_id>`

**Request Body:** Fuel entry fields to update (partial update supported)

**Response:** Updated fuel entry

### Delete Fuel Entry

**Endpoint:** `DELETE /api/fuel/<int:entry_id>`

**Response:** `{"message": "Fuel entry deleted successfully"}`

### Get Fuel Economy

**Endpoint:** `GET /api/fuel/economy`

**Query Parameters:**
- `vehicle_id` (required) - Vehicle to calculate MPG for

**Response:**
```json
{
  "mpg_data": [
    {
      "date": "2026-02-15",
      "mileage": 45000,
      "mpg": 28.5,
      "gallons": 12.5
    }
  ],
  "average_mpg": 28.5,
  "vehicle_id": 1
}
```

**Note:** Requires at least 2 fuel entries with `is_full_tank=true` to calculate MPG.

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | Success | Request completed successfully |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Validation error or missing required fields |
| `404` | Not Found | Resource not found |
| `500` | Internal Server Error | Server error |

---

## File Uploads

**Upload Directory:** `uploads/` (relative to backend root)

**Supported File Types:**
- Images: JPG, PNG, GIF, WEBP
- Documents: PDF, TXT, MD

**Max File Size:** 10MB (configurable in Flask app config)

**Endpoints:**
- `POST /api/upload` - Upload any file
- `POST /api/vehicles/<vehicle_id>/photos` - Upload vehicle photo

---

## Database Models

The API is backed by 12 SQLAlchemy models:

| Model | Description |
|-------|-------------|
| **Vehicle** | Vehicle information (make, model, year, VIN, mileage) |
| **VehiclePhoto** | Vehicle photo metadata (filename, primary flag) |
| **Service** | Maintenance/service records (date, mileage, cost, parts) |
| **ServiceInterval** | Recurring service intervals (interval miles/months) |
| **Reminder** | Service reminders (due date, status) |
| **Modification** | Vehicle modifications (status workflow, parts, cost) |
| **FaultCode** | VCDS diagnostic fault codes (status, dates) |
| **Cost** | Cost tracking (category, vendor, date) |
| **FuelEntry** | Fuel fill-up records (gallons, MPG calculation) |
| **Document** | Document/receipt metadata (file path, type) |
| **Note** | User notes (title, content) |
| **Guide** | How-to guides (steps, intervals, templates) |
| **Settings** | Application settings (key-value pairs) |

---

## Notes

- All dates are in ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`)
- All monetary values are in the configured currency (default: USD)
- All distances are in configured units (default: miles)
- Cascade delete is implemented for all vehicle relationships
- JSON arrays (e.g., `parts_used`, `parts`, `steps`) are stored as JSON strings
- Test mode support for data isolation (configured via Settings)

---

## Endpoint Summary

| Category | Endpoints |
|----------|-----------|
| Health | `GET /api/health` |
| Dashboard | `GET /api/dashboard` |
| Vehicles | `GET, POST, PUT, DELETE /api/vehicles`, `GET, POST /api/vehicles/export`, `POST /api/vehicles/import` |
| Photos | `GET, POST /api/vehicles/<id>/photos`, `DELETE /api/photos/<id>`, `POST /api/photos/<id>/primary` |
| Maintenance | `GET, POST, PUT, DELETE /api/maintenance`, `GET, POST /api/maintenance/intervals`, `GET, PUT, POST /api/maintenance/reminders`, `GET /api/maintenance/timeline` |
| Modifications | `GET, POST, PUT, DELETE /api/mods`, `PUT /api/mods/<id>/status` |
| VCDS | `GET, POST, PUT, DELETE /api/vcds`, `POST /api/vcds/parse`, `POST /api/vcds/import`, `POST /api/vcds/<id>/clear`, `POST /api/vcds/<id>/activate` |
| Costs | `GET, POST, PUT, DELETE /api/costs`, `GET /api/costs/summary` |
| Analytics | `GET /api/analytics/spending` |
| Fuel | `GET, POST, PUT, DELETE /api/fuel`, `GET /api/fuel/economy` |
| Documents | `GET, POST, PUT, DELETE /api/documents` |
| Upload | `POST /api/upload` |
| Notes | `GET, POST, PUT, DELETE /api/notes` |
| Settings | `GET, POST /api/settings`, `GET /api/settings/<key>`, `GET /api/settings/backup`, `POST /api/settings/restore` |
| Guides | `GET, POST, PUT, DELETE /api/guides`, `POST /api/guides/templates` |

**Total:** 52 endpoints across 14 categories
