# Cost Analysis Specification

**Related to:** JTBD-004

**Last Updated:** 2026-02-23

---

## Overview

The cost analysis system allows users to track and analyze all vehicle-related expenses across categories with filtering, summaries, and dashboard visualization.

---

## Basic Capability

### Cost Entity

**Fields:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `category` (string, e.g., "Fuel", "Maintenance", "Modification", "Insurance", "Registration")
- `amount` (decimal)
- `date` (date)
- `description` (text, optional)
- `vendor` (string, optional)
- `payment_method` (string, optional, e.g., "Credit Card", "Cash")
- `receipt_url` (string, optional, link to uploaded receipt)
- `odometer` (integer, optional, mileage at time of expense)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### CRUD Operations

**Create Cost:**
- Endpoint: `POST /api/costs`
- Required fields: `vehicle_id`, `category`, `amount`, `date`
- Optional fields: all others
- Returns: Created cost object

**Read Costs:**
- List all: `GET /api/costs`
- Filter by vehicle: `GET /api/costs?vehicle_id=<id>`
- Filter by category: `GET /api/costs?category=Fuel`
- Get one: `GET /api/costs/<id>`
- Returns: Cost object(s)

**Update Cost:**
- Endpoint: `PUT /api/costs/<id>`
- Accepts: Any cost fields
- Returns: Updated cost object

**Delete Cost:**
- Endpoint: `DELETE /api/costs/<id>`
- Returns: 204 No Content

---

## Enhanced Capability

### Category Filtering

**Filter by Category:**
- Endpoint: `GET /api/costs?category=Fuel`
- Multiple categories: `GET /api/costs?category=Fuel,Maintenance`
- Standard categories:
  - Fuel
  - Maintenance
  - Modification
  - Insurance
  - Registration
  - Taxes
  - Parking
  - Tolls
  - Repairs
  - Other

**Get Categories:**
- Endpoint: `GET /api/costs/categories`
- Returns: Array of unique categories used
- Optional: Include count and total per category

### Date Range Filtering

**Filter by Date Range:**
- Endpoint: `GET /api/costs?start_date=2024-01-01&end_date=2024-12-31`
- Filter by year: `GET /api/costs?year=2024`
- Filter by month: `GET /api/costs?year=2024&month=6`
- Combine with other filters: `GET /api/costs?vehicle_id=1&category=Fuel&year=2024`

**Date Filter Implementation:**
```python
@app.route('/api/costs', methods=['GET'])
def get_costs():
    vehicle_id = request.args.get('vehicle_id')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Cost.query
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    if category:
        categories = category.split(',')
        query = query.filter(Cost.category.in_(categories))
    
    if start_date:
        query = query.filter(Cost.date >= start_date)
    
    if end_date:
        query = query.filter(Cost.date <= end_date)
    
    return jsonify(query.order_by(Cost.date.desc()).all())
```

### Cost Summary

**Get Cost Summary:**
- Endpoint: `GET /api/costs/summary`
- Filters: `vehicle_id`, `start_date`, `end_date`, `category`
- Returns:
```json
{
  "total_cost": 5420.50,
  "count": 45,
  "by_category": {
    "Fuel": {"total": 2400.00, "count": 24},
    "Maintenance": {"total": 1520.50, "count": 8},
    "Modification": {"total": 1500.00, "count": 3}
  },
  "average_per_month": 451.71,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

**Monthly Breakdown:**
- Endpoint: `GET /api/costs/summary/monthly?vehicle_id=<id>&year=2024`
- Returns:
```json
{
  "months": [
    {"month": "2024-01", "total": 450.00, "by_category": {...}},
    {"month": "2024-02", "total": 380.50, "by_category": {...}}
  ]
}
```

---

## Advanced Capability

### Configurable Total Spend Categories

**Settings Entity:**
- `id` (integer, primary key)
- `key` (string, unique)
- `value` (text, JSON or string)
- `updated_at` (timestamp)

**Total Spend Settings:**
- `total_spend_include_fuel` (boolean, default true)
- `total_spend_include_maintenance` (boolean, default true)
- `total_spend_include_modification` (boolean, default true)
- `total_spend_include_insurance` (boolean, default false)
- `total_spend_include_registration` (boolean, default false)
- `total_spend_include_taxes` (boolean, default false)
- `total_spend_include_parking` (boolean, default false)
- `total_spend_include_tolls` (boolean, default false)

**Get Settings:**
- Endpoint: `GET /api/settings`
- Returns: All settings

**Update Settings:**
- Endpoint: `PUT /api/settings`
- Body: `{"total_spend_include_fuel": false}`
- Returns: Updated settings

**Dashboard Total Calculation:**
- Endpoint: `GET /api/dashboard`
- Uses settings to filter which categories are included
- Returns:
```json
{
  "total_costs": 3920.50,
  "total_costs_breakdown": {
    "Fuel": 2400.00,
    "Maintenance": 1520.50
  },
  "excluded_categories": ["Insurance", "Registration"]
}
```

### Dashboard Spending Charts

**Dashboard Chart Data:**
- Endpoint: `GET /api/analytics/spending?vehicle_id=<id>`
- Optional: `start_date`, `end_date`
- Returns:
```json
{
  "by_category": [
    {"category": "Fuel", "amount": 2400.00, "percentage": 61.2},
    {"category": "Maintenance", "amount": 1520.50, "percentage": 38.8}
  ],
  "by_month": [
    {"month": "2024-01", "amount": 450.00},
    {"month": "2024-02", "amount": 380.50}
  ],
  "total": 3920.50
}
```

**Chart Types Supported:**
- Pie chart: Category breakdown
- Bar chart: Monthly spending
- Line chart: Spending trend over time

### Cost Per Mile/KM

**Calculate Cost Per Mile:**
- Endpoint: `GET /api/costs/analysis/cost-per-mile?vehicle_id=<id>`
- Requires: Odometer readings or mileage tracking
- Returns:
```json
{
  "total_cost": 5420.50,
  "total_miles": 12000,
  "cost_per_mile": 0.45,
  "by_category": {
    "Fuel": {"cost_per_mile": 0.20},
    "Maintenance": {"cost_per_mile": 0.13}
  }
}
```

### Budget Tracking (Optional Enhancement)

**Budget Entity:**
- `id` (integer, primary key)
- `vehicle_id` (integer, foreign key)
- `category` (string)
- `budget_amount` (decimal, monthly budget)
- `month` (integer, 1-12)
- `year` (integer)

**Budget vs Actual:**
- Endpoint: `GET /api/costs/analysis/budget?vehicle_id=<id>&month=6&year=2024`
- Returns:
```json
{
  "month": "2024-06",
  "budget_total": 500.00,
  "actual_total": 450.00,
  "difference": 50.00,
  "by_category": {
    "Fuel": {"budget": 200.00, "actual": 180.00, "difference": 20.00},
    "Maintenance": {"budget": 300.00, "actual": 270.00, "difference": 30.00}
  }
}
```

---

## Acceptance Criteria

### Basic

- [ ] Create cost entry with required fields
- [ ] Update cost entry
- [ ] Delete cost entry
- [ ] List all costs
- [ ] Filter by vehicle_id
- [ ] Filter by category
- [ ] Get single cost details
- [ ] Validate required fields
- [ ] Return 404 for non-existent cost

### Enhanced

- [ ] Filter by multiple categories
- [ ] Filter by date range (start_date, end_date)
- [ ] Filter by year/month
- [ ] Combine multiple filters
- [ ] Get cost summary with totals
- [ ] Summary groups by category
- [ ] Summary includes count and average
- [ ] Monthly breakdown endpoint

### Advanced

- [ ] Settings control which categories included in total
- [ ] Dashboard uses settings for total calculation
- [ ] Dashboard shows category breakdown
- [ ] Analytics endpoint returns chart data
- [ ] Chart data supports date filtering
- [ ] Cost per mile calculation
- [ ] Cascade delete when vehicle deleted

---

## Edge Cases

### Validation

- Amount cannot be negative
- Date cannot be in the future
- Category cannot be empty
- Vehicle_id must reference existing vehicle

### Category Handling

- Categories are case-insensitive (normalize to title case)
- Unknown categories are allowed (not restricted to predefined list)
- Category names are trimmed of whitespace

### Date Filtering

- If only year provided, use full year (Jan 1 - Dec 31)
- If year and month provided, use full month
- start_date defaults to beginning of time if not provided
- end_date defaults to today if not provided

### Total Calculation

- Exclude costs with null amount
- Handle decimal precision (2 decimal places)
- Round percentages to 1 decimal place

---

## Data Relationships

```
Vehicle (1) ──→ (many) Cost
```

---

## API Response Format

### Cost Object

```json
{
  "id": 1,
  "vehicle_id": 1,
  "category": "Fuel",
  "amount": 65.50,
  "date": "2024-06-15",
  "description": "Full tank premium",
  "vendor": "Shell",
  "payment_method": "Credit Card",
  "receipt_url": "/uploads/receipts/1/receipt.pdf",
  "odometer": 45000,
  "created_at": "2024-06-15T18:30:00Z",
  "updated_at": "2024-06-15T18:30:00Z"
}
```

### Cost Summary Response

```json
{
  "total_cost": 5420.50,
  "count": 45,
  "by_category": {
    "Fuel": {"total": 2400.00, "count": 24},
    "Maintenance": {"total": 1520.50, "count": 8},
    "Modification": {"total": 1500.00, "count": 3}
  },
  "average_per_month": 451.71,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

### Analytics Spending Response

```json
{
  "by_category": [
    {"category": "Fuel", "amount": 2400.00, "percentage": 61.2},
    {"category": "Maintenance", "amount": 1520.50, "percentage": 38.8}
  ],
  "by_month": [
    {"month": "2024-01", "amount": 450.00},
    {"month": "2024-02", "amount": 380.50},
    {"month": "2024-03", "amount": 520.75}
  ],
  "total": 3920.50
}
```

---

## Notes

- Costs can be manually entered or imported from other systems
- Categories are flexible (not restricted to predefined list)
- Settings allow customization of what's included in totals
- Dashboard charts use Chart.js for visualization
