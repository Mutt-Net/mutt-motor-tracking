# Cost Analysis Specification

**Related to:** JTBD-001 (Service record tracking), JTBD-003 (Modification tracking)

**Description:** Track and analyze vehicle expenses across categories. Provide summary views, dashboard charts, and configurable total spend calculations.

---

## Capability Depths

### Basic

Minimal viable implementation for cost tracking:

- Create cost entries with:
  - Date
  - Category (fuel, insurance, tax, maintenance, mods, etc.)
  - Amount
  - Description
- View costs sorted by date
- Filter by vehicle

### Enhanced

Additional features for comprehensive analysis:

- Summary by category with totals
- Date filtering (start_date, end_date)
- Cost per mile calculations
- Dashboard charts (Chart.js integration)

### Advanced

Edge cases and integrations:

- Configurable what's included in 'total spend'
- Cost breakdown by subcategory
- Trend analysis over time
- Export cost data to CSV

---

## Data Model

### Cost Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| vehicle_id | Integer | Foreign Key -> vehicles.id (CASCADE) | Parent vehicle |
| date | Date | | Expense date |
| category | String(50) | | Category (fuel, insurance, tax, etc.) |
| amount | Float | | Cost amount |
| description | Text | | Expense description |
| test_key | String(50) | Nullable, Indexed | Test data isolation key |
| created_at | DateTime | Default: UTC now | Record creation timestamp |

---

## API Endpoints

### Cost CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/costs?vehicle_id= | List costs |
| POST | /api/costs | Create cost entry |
| GET | /api/costs/{id} | Get cost by ID |
| PUT | /api/costs/{id} | Update cost entry |
| DELETE | /api/costs/{id} | Delete cost entry |

### Cost Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/costs/summary?vehicle_id=&start_date=&end_date= | Get summary by category |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard | Get aggregated stats including costs |
| GET | /api/dashboard/{vehicle_id} | Get stats for specific vehicle |

---

## Acceptance Criteria

### Core Functionality

- [ ] Can create cost entry with all fields (date, category, amount, description)
- [ ] Can retrieve costs filtered by vehicle_id
- [ ] Can update cost entry
- [ ] Can delete cost entry
- [ ] Costs sorted by date descending

### Category Tracking

- [ ] Categories include: fuel, insurance, tax, maintenance, mods, registration, parking, other
- [ ] Category is free-form text (no enforcement)
- [ ] Costs can be filtered by category:
  - GET /api/costs?vehicle_id=1&category=fuel returns only fuel costs

### Summary by Category

- [ ] Summary endpoint returns totals grouped by category
- [ ] Summary accepts vehicle_id filter
- [ ] Summary accepts date range filtering:
  - start_date (YYYY-MM-DD)
  - end_date (YYYY-MM-DD)
- [ ] Summary returns:
  - category
  - total_amount
  - count (number of entries)

### Dashboard Integration

- [ ] Dashboard returns correct cost aggregations:
  - Total fuel cost
  - Total maintenance cost
  - Total mod cost
  - Total insurance cost
  - Total tax cost
  - Grand total (based on settings)
- [ ] Dashboard respects settings for total_spend_include_*:
  - total_spend_include_fuel
  - total_spend_include_maintenance
  - total_spend_include_mods
  - total_spend_include_insurance
  - total_spend_include_tax
- [ ] Dashboard returns data for charts:
  - Cost by category (pie chart data)
  - Spending over time (line chart data)

### Date Filtering

- [ ] Cost list accepts start_date and end_date parameters
- [ ] Summary accepts start_date and end_date parameters
- [ ] Date filtering is inclusive (>= start_date AND <= end_date)
- [ ] Invalid date format returns error

### Validation & Error Handling

- [ ] Cost creation validates required fields (vehicle_id, amount)
- [ ] Amount must be positive number
- [ ] Invalid cost ID returns 404
- [ ] All error responses return {'error': 'message'} format
- [ ] Date format validated (YYYY-MM-DD)

---

## Cost Categories

| Category | Description | Included in Total by Default |
|----------|-------------|------------------------------|
| fuel | Fuel purchases | Yes |
| maintenance | Service and repairs | Yes |
| mods | Modifications and upgrades | Yes |
| insurance | Insurance premiums | Configurable |
| tax | Vehicle tax | Configurable |
| registration | Registration fees | Configurable |
| parking | Parking fees | No |
| other | Miscellaneous | No |

---

## Settings Integration

### Total Spend Configuration

Settings that control what's included in dashboard total spend:

| Setting Key | Type | Default |
|-------------|------|---------|
| total_spend_include_fuel | boolean | true |
| total_spend_include_maintenance | boolean | true |
| total_spend_include_mods | boolean | true |
| total_spend_include_insurance | boolean | false |
| total_spend_include_tax | boolean | false |
| total_spend_include_registration | boolean | false |

**Note:** Settings accessed via /api/settings endpoint

---

## Frontend Integration

### Costs View

- Costs list with filter by vehicle and category
- Add/edit cost form with all fields
- Date range picker
- Category summary table
- Cost per mile display

### Dashboard View

- Total spend card (configurable categories)
- Spending by category pie chart (Chart.js)
- Monthly spending trend line chart
- Recent costs list

---

## Notes

- Costs aggregated in dashboard along with other expense types
- Summary endpoint useful for reports and analytics
- Date filtering enables custom period analysis
- Test mode support via test_key field for data isolation
- Category is free-form but UI should suggest common categories
