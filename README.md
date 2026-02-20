# MuttLogbook

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](VERSION)
[![Python](https://img.shields.io/badge/python-3.10+-green)](requirements.txt)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

Vehicle service logbook for VW EOS (and other vehicles). Track maintenance, modifications, costs, fuel economy, and VCDS fault codes.

## Features

- **Vehicle Management** - Multiple vehicles with detailed profiles (VIN, mileage, engine, transmission)
- **Service Tracking** - Full maintenance history with cost, labor, and parts tracking
- **Modifications** - Track planned, in-progress, and completed mods
- **Cost Analysis** - Categorized expenses with analytics dashboard
- **Fuel Tracking** - Log fuel entries with MPG calculations
- **VCDS Fault Codes** - Import and parse VCDS fault code scans
- **Service Intervals** - Automatic reminders based on mileage/time
- **Data Export** - CSV export for all vehicle data

## Requirements

- Python 3.10+
- SQLite 3
- Flask 3.x

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Mutt-Net/mutt-logbook.git
cd mutt-logbook

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
# Start the server
python -m backend.app

# Open in browser
http://localhost:5000
```

### Generate Test Data

```bash
# Create sample data for testing
curl -X POST http://localhost:5000/api/seed-test-data -H "Content-Type: application/json" -d '{"vehicle_id": 1}'
```

## Docker

Docker support coming in v1.1.0.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/vehicles` | List/Create vehicles |
| GET/PUT/DELETE | `/api/vehicles/<id>` | Get/Update/Delete vehicle |
| GET/POST | `/api/maintenance` | List/Create service records |
| GET/POST | `/api/mods` | List/Create modifications |
| GET/POST | `/api/costs` | List/Create expenses |
| GET/POST | `/api/fuel` | List/Create fuel entries |
| GET/POST | `/api/vcds/parse` | Parse VCDS fault codes |
| POST | `/api/vcds/import` | Import parsed faults |
| POST | `/api/seed-test-data` | Generate test data |
| GET | `/api/analytics` | Get analytics data |
| GET | `/api/dashboard` | Get dashboard summary |

## VCDS Import

Supports three import methods:

1. **Paste Text** - Paste VCDS scan output directly
2. **Upload File** - Upload .txt or .csv file
3. **Manual Entry** - Enter fault codes manually

Example VCDS format:
```
08 Auto HVAC
00819 High Pressure Sensor

19 CAN Gateway
03582 Radio no signal
```

## Project Structure

```
mutt-logbook/
├── backend/
│   ├── app.py          # Flask application
│   ├── routes.py       # API endpoints
│   ├── models.py       # Database models
│   └── tests/          # Test suite
├── frontend/
│   ├── index.html      # Main HTML
│   ├── js/app.js       # Frontend JavaScript
│   └── css/style.css   # Styles
├── database/
│   └── logbook.db      # SQLite database
├── docs/               # Documentation
└── uploads/            # File uploads
```

## Testing

```bash
# Run tests
python -m pytest -v

# Run with coverage
python -m pytest --cov=backend --cov-report=term
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Author

Mutt-Net - https://github.com/Mutt-Net
