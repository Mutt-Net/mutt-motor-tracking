# MuttLogbook Rebuild Planning Document
## Spring Boot + React/TypeScript v1.0

**Created:** 2026-02-14  
**Status:** PLANNING  
**Target Version:** v1.0

---

## 1. Executive Summary

### 1.1 Project Overview
Rebuild the existing MuttLogbook Flask application into a modern, production-ready stack:
- **Backend:** Spring Boot 3.x with Java 17
- **Frontend:** React 18 with TypeScript + Vite
- **Database:** PostgreSQL (new schema design)
- **Architecture:** Polyrepo (separate backend/frontend repos)
- **API:** RESTful API

### 1.2 Goals
1. Establish proper separation of concerns (layered architecture)
2. Add comprehensive test coverage
3. Improve maintainability and scalability
4. Enable future authentication/authorization
5. Full feature parity with current application

---

## 2. Repository Structure

### 2.1 Backend Repository
```
mutt-logbook-spring/
├── pom.xml
├── README.md
├── .gitignore
└── src/
    └── main/
        ├── java/com/muttnet/logbook/
        │   ├── MuttLogbookApplication.java
        │   ├── config/
        │   │   ├── SecurityConfig.java
        │   │   ├── CorsConfig.java
        │   │   ├── JacksonConfig.java
        │   │   └── ValidationConfig.java
        │   ├── controller/
        │   │   ├── VehicleController.java
        │   │   ├── MaintenanceController.java
        │   │   ├── ModController.java
        │   │   ├── CostController.java
        │   │   ├── NoteController.java
        │   │   ├── VcdsController.java
        │   │   ├── GuideController.java
        │   │   ├── DashboardController.java
        │   │   ├── AnalyticsController.java
        │   │   └── PhotoController.java
        │   ├── service/
        │   │   ├── VehicleService.java
        │   │   ├── MaintenanceService.java
        │   │   ├── ModService.java
        │   │   ├── CostService.java
        │   │   ├── NoteService.java
        │   │   ├── VcdsService.java
        │   │   ├── GuideService.java
        │   │   ├── DashboardService.java
        │   │   └── AnalyticsService.java
        │   ├── repository/
        │   │   ├── VehicleRepository.java
        │   │   ├── MaintenanceRepository.java
        │   │   ├── ModRepository.java
        │   │   ├── CostRepository.java
        │   │   ├── NoteRepository.java
        │   │   ├── VcdsFaultRepository.java
        │   │   ├── GuideRepository.java
        │   │   └── VehiclePhotoRepository.java
        │   ├── model/
        │   │   ├── entity/
        │   │   │   ├── Vehicle.java
        │   │   │   ├── Maintenance.java
        │   │   │   ├── Mod.java
        │   │   │   ├── Cost.java
        │   │   │   ├── Note.java
        │   │   │   ├── VcdsFault.java
        │   │   │   ├── Guide.java
        │   │   │   └── VehiclePhoto.java
        │   │   └── enums/
        │   │       ├── ModStatus.java
        │   │       └── FaultStatus.java
        │   ├── dto/
        │   │   ├── request/
        │   │   │   ├── VehicleRequest.java
        │   │   │   ├── MaintenanceRequest.java
        │   │   │   ├── ModRequest.java
        │   │   │   ├── CostRequest.java
        │   │   │   ├── NoteRequest.java
        │   │   │   ├── VcdsFaultRequest.java
        │   │   │   ├── GuideRequest.java
        │   │   │   └── ImportRequest.java
        │   │   └── response/
        │   │       ├── VehicleResponse.java
        │   │       ├── MaintenanceResponse.java
        │   │       ├── ModResponse.java
        │   │       ├── CostResponse.java
        │   │       ├── NoteResponse.java
        │   │       ├── VcdsFaultResponse.java
        │   │       ├── GuideResponse.java
        │   │       ├── DashboardResponse.java
        │   │       ├── AnalyticsResponse.java
        │   │       └── ApiError.java
        │   ├── exception/
        │   │   ├── GlobalExceptionHandler.java
        │   │   ├── ResourceNotFoundException.java
        │   │   └── BadRequestException.java
        │   └── util/
        │       ├── JsonHelper.java
        │       └── DateHelper.java
        └── resources/
            ├── application.yml
            ├── application-dev.yml
            ├── application-prod.yml
            └── data.sql
```

### 2.2 Frontend Repository
```
mutt-logbook-react/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── README.md
├── .gitignore
├── env.d.ts
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/
    │   ├── client.ts
    │   ├── vehicles.ts
    │   ├── maintenance.ts
    │   ├── mods.ts
    │   ├── costs.ts
    │   ├── notes.ts
    │   ├── vcds.ts
    │   ├── guides.ts
    │   ├── dashboard.ts
    │   └── analytics.ts
    ├── components/
    │   ├── common/
    │   │   ├── Button.tsx
    │   │   ├── Input.tsx
    │   │   ├── Select.tsx
    │   │   ├── Modal.tsx
    │   │   ├── Card.tsx
    │   │   ├── Badge.tsx
    │   │   ├── LoadingSpinner.tsx
    │   │   └── ErrorMessage.tsx
    │   ├── layout/
    │   │   ├── Header.tsx
    │   │   ├── Navbar.tsx
    │   │   ├── Footer.tsx
    │   │   └── Sidebar.tsx
    │   ├── vehicle/
    │   │   ├── VehicleSelector.tsx
    │   │   ├── VehicleForm.tsx
    │   │   └── VehicleCard.tsx
    │   ├── dashboard/
    │   │   ├── StatCard.tsx
    │   │   ├── StatsGrid.tsx
    │   │   ├── AlertBanner.tsx
    │   │   └── RecentActivity.tsx
    │   ├── charts/
    │   │   ├── CategoryChart.tsx
    │   │   ├── TrendChart.tsx
    │   │   ├── TimelineChart.tsx
    │   │   └── YearlyChart.tsx
    │   └── forms/
    │       ├── MaintenanceForm.tsx
    │       ├── ModForm.tsx
    │       ├── CostForm.tsx
    │       ├── NoteForm.tsx
    │       ├── GuideForm.tsx
    │       └── VcdsForm.tsx
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Vehicle.tsx
    │   ├── Profiles.tsx
    │   ├── Maintenance.tsx
    │   ├── Mods.tsx
    │   ├── Costs.tsx
    │   ├── Notes.tsx
    │   ├── Guides.tsx
    │   ├── Vcds.tsx
    │   └── Analytics.tsx
    ├── types/
    │   ├── vehicle.ts
    │   ├── maintenance.ts
    │   ├── mod.ts
    │   ├── cost.ts
    │   ├── note.ts
    │   ├── vcds.ts
    │   ├── guide.ts
    │   ├── dashboard.ts
    │   ├── analytics.ts
    │   └── index.ts
    ├── hooks/
    │   ├── useVehicles.ts
    │   ├── useMaintenance.ts
    │   ├── useDashboard.ts
    │   ├── useAnalytics.ts
    │   └── useLocalStorage.ts
    ├── store/
    │   ├── vehicleStore.ts
    │   └── uiStore.ts
    ├── utils/
    │   ├── formatters.ts
    │   ├── validators.ts
    │   └── helpers.ts
    └── styles/
        ├── index.css
        ├── variables.css
        └── components/
```

---

## 3. Database Schema

### 3.1 PostgreSQL Schema

```sql
-- =====================================================
-- MuttLogbook PostgreSQL Schema v1.0
-- =====================================================

-- ENUMS
CREATE TYPE mod_status AS ENUM ('planned', 'in_progress', 'completed');
CREATE TYPE fault_status AS ENUM ('active', 'cleared');

-- VEHICLES TABLE
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    vin VARCHAR(17) UNIQUE,
    year INTEGER,
    engine VARCHAR(100),
    transmission VARCHAR(50),
    mileage INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MAINTENANCE TABLE
CREATE TABLE maintenance (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    mileage INTEGER,
    category VARCHAR(50),
    description TEXT,
    parts_used JSONB,
    labor_hours DECIMAL(5,2),
    cost DECIMAL(10,2),
    shop_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MODS TABLE
CREATE TABLE mods (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    date DATE,
    mileage INTEGER,
    category VARCHAR(50),
    description TEXT,
    parts JSONB,
    cost DECIMAL(10,2),
    status mod_status DEFAULT 'planned',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- COSTS TABLE
CREATE TABLE costs (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    date DATE,
    category VARCHAR(50),
    amount DECIMAL(10,2),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- NOTES TABLE
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    date DATE,
    title VARCHAR(200),
    content TEXT,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- VCDS FAULTS TABLE
CREATE TABLE vcds_faults (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    address VARCHAR(50),
    component VARCHAR(200),
    fault_code VARCHAR(20),
    description TEXT,
    status fault_status DEFAULT 'active',
    detected_date DATE,
    cleared_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GUIDES TABLE
CREATE TABLE guides (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    content TEXT,
    interval_miles INTEGER,
    interval_months INTEGER,
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- VEHICLE PHOTOS TABLE
CREATE TABLE vehicle_photos (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    filename VARCHAR(200),
    caption VARCHAR(500),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_maintenance_vehicle ON maintenance(vehicle_id);
CREATE INDEX idx_maintenance_date ON maintenance(date);
CREATE INDEX idx_mods_vehicle ON mods(vehicle_id);
CREATE INDEX idx_mods_status ON mods(status);
CREATE INDEX idx_costs_vehicle ON costs(vehicle_id);
CREATE INDEX idx_costs_category ON costs(category);
CREATE INDEX idx_notes_vehicle ON notes(vehicle_id);
CREATE INDEX idx_vcds_vehicle ON vcds_faults(vehicle_id);
CREATE INDEX idx_vcds_status ON vcds_faults(status);
CREATE INDEX idx_guides_vehicle ON guides(vehicle_id);
CREATE INDEX idx_guides_template ON guides(is_template);
```

---

## 4. API Specification

### 4.1 API Endpoints Summary

| Resource | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| `/api/vehicles` | List all | Create | - | - |
| `/api/vehicles/{id}` | Get one | - | Update | Delete |
| `/api/vehicles/{id}/export` | Export | - | - | - |
| `/api/vehicles/import` | - | Import | - | - |
| `/api/maintenance` | List | Create | - | - |
| `/api/maintenance/{id}` | Get one | - | Update | Delete |
| `/api/mods` | List | Create | - | - |
| `/api/mods/{id}` | Get one | - | Update | Delete |
| `/api/costs` | List | Create | - | - |
| `/api/costs/{id}` | Get one | - | Update | Delete |
| `/api/costs/summary` | Summary | - | - | - |
| `/api/notes` | List | Create | - | - |
| `/api/notes/{id}` | Get one | - | Update | Delete |
| `/api/vcds` | List | Create | - | - |
| `/api/vcds/{id}` | Get one | - | Update | Delete |
| `/api/vcds/import` | - | Bulk import | - | - |
| `/api/vcds/parse` | - | Parse text | - | - |
| `/api/guides` | List | Create | - | - |
| `/api/guides/{id}` | Get one | - | Update | Delete |
| `/api/guides/templates` | List templates | Create templates | - | - |
| `/api/dashboard` | Dashboard data | - | - | - |
| `/api/analytics` | Analytics data | - | - | - |

### 4.2 Detailed API Contracts

#### 4.2.1 Vehicles

**GET /api/vehicles**
```json
Response: [
  {
    "id": 1,
    "name": "VW EOS",
    "vin": "WVWZZZ1FZ7V033393",
    "year": 2007,
    "engine": "2.0 R4/4V TFSI (AXX)",
    "transmission": "6-speed Manual",
    "mileage": 116000
  }
]
```

**POST /api/vehicles**
```json
Request: {
  "name": "VW EOS",
  "vin": "WVWZZZ1FZ7V033393",
  "year": 2007,
  "engine": "2.0 R4/4V TFSI (AXX)",
  "transmission": "6-speed Manual",
  "mileage": 116000
}
Response: { "id": 1 }
```

**PUT /api/vehicles/{id}**
```json
Request: {
  "name": "VW EOS",
  "mileage": 117000
}
Response: { "success": true }
```

**DELETE /api/vehicles/{id}**
```json
Response: { "success": true }
```

#### 4.2.2 Maintenance

**GET /api/maintenance?vehicle_id={id}**
```json
Response: [
  {
    "id": 1,
    "vehicleId": 1,
    "date": "2024-01-15",
    "mileage": 115000,
    "category": "oil_change",
    "description": "Oil change with filter",
    "partsUsed": ["Oil filter", "5W-30 synthetic"],
    "laborHours": 1.0,
    "cost": 75.00,
    "shopName": "Local Garage",
    "notes": ""
  }
]
```

**POST /api/maintenance**
```json
Request: {
  "vehicleId": 1,
  "date": "2024-01-15",
  "mileage": 115000,
  "category": "oil_change",
  "description": "Oil change with filter",
  "partsUsed": ["Oil filter", "5W-30 synthetic"],
  "laborHours": 1.0,
  "cost": 75.00,
  "shopName": "Local Garage",
  "notes": ""
}
Response: { "id": 1 }
```

#### 4.2.3 Dashboard

**GET /api/dashboard?vehicle_id={id}**
```json
Response: {
  "totalSpent": 1751.79,
  "maintenanceCost": 1200.00,
  "modsCost": 400.00,
  "otherCosts": 151.79,
  "recentMaintenance": [
    {
      "date": "2024-01-15",
      "category": "oil_change",
      "description": "Oil change"
    }
  ],
  "activeFaults": 2
}
```

#### 4.2.4 Analytics

**GET /api/analytics?vehicle_id={id}&start_date={date}&end_date={date}**
```json
Response: {
  "monthlySpending": {
    "2024-01": 450.00,
    "2024-02": 200.00
  },
  "yearlySpending": {
    "2023": 1200.00,
    "2024": 551.79
  },
  "categorySpending": {
    "oil_change": 300.00,
    "brakes": 450.00
  },
  "totalSpent": 1751.79,
  "serviceIntervals": {
    "oilChange": { "miles": 5000, "months": 6 },
    "brakes": { "miles": 20000, "months": 24 },
    "tireRotation": { "miles": 7500, "months": 6 },
    "inspection": { "miles": 15000, "months": 12 }
  },
  "lastService": {
    "oilChange": { "date": "2024-01-15", "mileage": 115000 }
  },
  "currentMileage": 116000
}
```

---

## 5. Implementation Roadmap

### Phase 1: Backend Foundation (Week 1)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Initialize Spring Boot project | `pom.xml`, base project structure |
| 2 | Configure PostgreSQL connection | `application.yml`, Entity definitions |
| 3 | Create entity classes | 8 JPA entities with relationships |
| 4 | Create repository interfaces | Spring Data JPA repositories |
| 5 | Implement Vehicle CRUD | Controller + Service + Tests |

### Phase 2: Backend Services (Week 2)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Implement Maintenance CRUD | Full CRUD with validation |
| 2 | Implement Mods CRUD | Full CRUD with status enum |
| 3 | Implement Costs + Summary | CRUD + aggregation endpoint |
| 4 | Implement Notes CRUD | Full CRUD |
| 5 | Implement VCDS endpoints | CRUD + import + parse |

### Phase 3: Backend Analytics (Week 3)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Implement Guides CRUD | Full CRUD + templates |
| 2 | Implement Dashboard | Aggregated data endpoint |
| 3 | Implement Analytics | Complex queries, date filtering |
| 4 | Import/Export endpoints | JSON import/export |
| 5 | Exception handling + tests | Global error handling, test coverage |

### Phase 4: Frontend Foundation (Week 4)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Initialize React + TS project | Vite + TypeScript setup |
| 2 | Set up API client | Axios instance with interceptors |
| 3 | Create TypeScript types | Type definitions matching DTOs |
| 4 | Build common components | Button, Modal, Form, Card |
| 5 | Set up routing | React Router configuration |

### Phase 5: Frontend Pages (Week 5-6)

| Week | Focus | Pages |
|------|-------|-------|
| 5 | Core pages | Dashboard, Vehicle, Profiles |
| 5 | Data pages | Maintenance, Mods, Costs |
| 6 | Additional pages | Notes, Guides, VCDS |
| 6 | Analytics | Charts integration |

### Phase 6: Testing & Polish (Week 7)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Integration testing | Test all 52 endpoints |
| 3-4 | Bug fixes | Fix any issues found |
| 5 | Performance optimization | Load time improvements |
| 5 | Documentation | API docs, README |
| 6 | Deployment prep | Docker, CI/CD pipeline |

---

## 6. Technology Stack Summary

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Spring Boot | 3.2.x |
| Language | Java | 17 |
| Database | PostgreSQL | 15+ |
| ORM | Spring Data JPA | - |
| Validation | Jakarta Validation | 3.0 |
| JSON | Jackson | - |
| Build | Maven | 3.9+ |
| Testing | JUnit 5 + Mockito | - |

### Frontend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | React | 18.x |
| Language | TypeScript | 5.x |
| Build | Vite | 5.x |
| HTTP | Axios | 1.6.x |
| Routing | React Router | 6.x |
| Charts | Recharts | 2.x |
| State | Zustand | 4.x |
| CSS | CSS Modules / Vanilla CSS | - |
| Testing | Vitest + React Testing Library | - |

---

## 7. Feature Parity Checklist

| Feature | Current | New Backend | New Frontend |
|---------|---------|-------------|--------------|
| Vehicle CRUD | ✅ | ✅ | ✅ |
| Vehicle export/import | ✅ | ✅ | ✅ |
| Maintenance log | ✅ | ✅ | ✅ |
| Mods tracking | ✅ | ✅ | ✅ |
| Cost tracking | ✅ | ✅ | ✅ |
| Cost summary | ✅ | ✅ | ✅ |
| VCDS faults | ✅ | ✅ | ✅ |
| VCDS import | ✅ | ✅ | ✅ |
| VCDS parse | ✅ | ✅ | ✅ |
| Guides | ✅ | ✅ | ✅ |
| Guide templates | ✅ | ✅ | ✅ |
| Notes/Journal | ✅ | ✅ | ✅ |
| Dashboard stats | ✅ | ✅ | ✅ |
| Analytics charts | ✅ | ✅ | ✅ |
| Service intervals | ✅ | ✅ | ✅ |
| Authentication | ❌ | Future | Future |
| Unit tests | ❌ | ✅ | ✅ |
| API documentation | ❌ | ✅ (Swagger) | - |

---

## 8. Open Questions / Trade-offs

1. **Authentication:** Should v1.0 include basic auth/JWT, or defer to v2.0?
2. **Deployment:** Docker Compose for local, or separate containers?
3. **CI/CD:** GitHub Actions workflows needed?
4. **Real-time features:** WebSockets for live updates (future)?
5. **File uploads:** Photos for vehicles - local storage or S3?

---

**Document Version:** 1.0  
**Next Review:** Before implementation begins
