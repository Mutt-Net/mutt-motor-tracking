# Project Specification

## Overview

**Project Name:** Mutt Motor Tracking

**Description:** A personal vehicle management application for tracking maintenance, modifications, costs, and diagnostics across multiple vehicles.

**Repository:** Local development

---

## Audience & Jobs to Be Done

### Primary Audience

**Who:** Vehicle enthusiasts and owners managing multiple cars/motorcycles

**Context:** Need to track service history, upcoming maintenance, modifications, fuel costs, and diagnostic codes in one centralized system

### Jobs to Be Done

| JTBD ID | Statement | Desired Outcome |
|---------|-----------|-----------------|
| JTBD-001 | When I own multiple vehicles, I want to track all service and maintenance in one place, so I can stay on top of upcoming maintenance and avoid costly repairs | Complete service history with automated reminders |
| JTBD-002 | When I modify my vehicles, I want to document all changes and costs, so I can track the total investment and resale value | Full modification log with cost tracking |
| JTBD-003 | When I diagnose issues, I want to store and track fault codes, so I can monitor recurring problems and repair progress | Fault code history with status tracking |
| JTBD-004 | When I maintain my vehicles, I want to analyze total ownership costs, so I can budget appropriately and understand depreciation | Cost breakdown by category and vehicle |

---

## Topics of Concern (Activities)

### Activity: vehicle-management

**Related to:** JTBD-001

**Description:** Add, edit, and manage vehicle profiles with photos and metadata

**Capability Depths:**
- **Basic:** CRUD operations for vehicles (make, model, year, VIN, mileage)
- **Enhanced:** Photo upload and management, primary photo selection
- **Advanced:** Import/export vehicle data with all related records

**Acceptance Criteria:**
- [ ] Create, read, update, delete vehicles
- [ ] Store vehicle metadata (VIN, license plate, color, purchase info)
- [ ] Upload and manage vehicle photos
- [ ] Export vehicle data to JSON/CSV
- [ ] Import vehicle data from JSON backup

---

### Activity: service-tracking

**Related to:** JTBD-001

**Description:** Log and track all maintenance and service activities

**Capability Depths:**
- **Basic:** Manual service entry with date, mileage, description, cost
- **Enhanced:** Service intervals with automatic reminders, parts used tracking
- **Advanced:** Timeline visualization with overdue/upcoming/ok status

**Acceptance Criteria:**
- [ ] Log service entries with full details
- [ ] Track service intervals and generate reminders
- [ ] Display maintenance timeline with status indicators
- [ ] Cascade delete services when vehicle deleted
- [ ] Store parts used as JSON array

---

### Activity: modification-tracking

**Related to:** JTBD-002

**Description:** Document all vehicle modifications with status workflow

**Capability Depths:**
- **Basic:** Manual mod entry with name, description, cost
- **Enhanced:** Status workflow (planned → in_progress → completed), parts tracking
- **Advanced:** Cost aggregation, installation notes, vendor links

**Acceptance Criteria:**
- [ ] Create modifications with status workflow
- [ ] Track modification costs and parts
- [ ] Filter modifications by status
- [ ] Aggregate mod costs in dashboard
- [ ] Store parts as JSON array

---

### Activity: vcds-diagnostics

**Related to:** JTBD-003

**Description:** Parse, import, and track VCDS diagnostic fault codes

**Capability Depths:**
- **Basic:** Manual fault code entry with description
- **Enhanced:** Parse VCDS text output, import fault codes automatically
- **Advanced:** Fault status tracking (active/cleared), detection/clear date tracking

**Acceptance Criteria:**
- [ ] Parse VCDS diagnostic text output
- [ ] Import fault codes from parsed data
- [ ] Manually add/edit fault codes
- [ ] Mark faults as cleared with date
- [ ] Track fault detection and clear dates

---

### Activity: cost-analysis

**Related to:** JTBD-004

**Description:** Track and analyze all vehicle-related expenses

**Capability Depths:**
- **Basic:** Manual cost entry with category, amount, date
- **Enhanced:** Category filtering, date range filtering, summary reports
- **Advanced:** Configurable total spend categories, dashboard charts

**Acceptance Criteria:**
- [ ] Log costs with category and metadata
- [ ] Filter costs by date range and category
- [ ] Display cost summary by category
- [ ] Configurable settings for what's included in totals
- [ ] Dashboard charts showing spending breakdown

---

### Activity: fuel-tracking

**Related to:** JTBD-001

**Description:** Track fuel fill-ups and calculate fuel economy

**Capability Depths:**
- **Basic:** Manual fuel entry with date, mileage, gallons, price
- **Enhanced:** Station tracking, fuel economy (MPG) calculations
- **Advanced:** Fuel economy trends over time, cost per mile

**Acceptance Criteria:**
- [ ] Log fuel fill-ups with full details
- [ ] Calculate MPG from fuel entries
- [ ] Track fuel station names
- [ ] Display fuel economy trends

---

### Activity: documentation

**Related to:** JTBD-001

**Description:** Store and organize vehicle documents, receipts, and guides

**Capability Depths:**
- **Basic:** Manual document entry with metadata
- **Enhanced:** File upload for receipts and documents
- **Advanced:** Guide templates with interval tracking

**Acceptance Criteria:**
- [ ] Upload and store document files
- [ ] Link documents to vehicles
- [ ] Store maintenance guide templates
- [ ] Track guide intervals (miles/months)

---

## Technical Constraints

| Constraint | Description |
|------------|-------------|
| **Language** | Python (backend), JavaScript (frontend) |
| **Runtime** | Python 3.10+, Modern browser |
| **Database** | SQLite with SQLAlchemy ORM |
| **External Services** | None (local application) |
| **Deployment** | Local Flask server |

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│     API      │────▶│  Database   │
│ (Vanilla JS)│     │   (Flask)    │     │   (SQLite)  │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Key Components

| Component | Responsibility | Location |
|-----------|----------------|----------|
| Flask API | REST endpoints, business logic | `backend/routes.py` |
| SQLAlchemy Models | Data schema, relationships | `backend/models.py` |
| Vanilla JS SPA | UI, data visualization | `frontend/index.html` |
| Test Suite | pytest tests | `backend/tests/` |

---

## Build & Test Commands

| Command | Purpose |
|---------|---------|
| `python -m pytest` | Run all tests |
| `python -m pytest --cov=backend` | Run tests with coverage |
| `python backend/app.py` | Start Flask server |

---

## Existing Conventions

### Code Style

- Python: Black + isort formatting
- JavaScript: ESLint recommended

### Project Structure

```
project-root/
├── backend/          # Flask API and models
├── backend/tests/    # pytest test suite
├── frontend/         # Vanilla JS SPA
├── specs/            # Detailed requirements
└── docs/             # Documentation
```

### Naming Conventions

- Files: snake_case.py (Python), kebab-case.html (HTML)
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

---

## Non-Goals

What this project explicitly does NOT do:

- Multi-user authentication (single user, local only)
- Cloud synchronization (local database only)
- Mobile app (web browser only)
- Integration with external services (no APIs except VCDS import)

---

## Future Considerations

Nice-to-haves for later (not in current scope):

- Photo gallery with drag-and-drop reordering
- Service reminder email/SMS notifications
- Export to PDF reports
- Barcode scanning for parts
- Integration with auto parts stores

---

## Notes

- Application is designed for personal use (single tenant)
- Test mode support for isolating test data from production
- Dark theme UI preferred
- Chart.js for data visualization
- localStorage for vehicle selection persistence
