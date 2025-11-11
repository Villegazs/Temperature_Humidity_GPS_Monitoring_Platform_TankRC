# Project Architecture

## Overview
This project implements a complete FIWARE-based IoT platform for monitoring temperature, humidity, and GPS tracking with intelligent irrigation recommendations. The architecture follows a modular microservices design for scalability and maintainability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌────────────────┐                                                  │
│  │   Web Browser  │ ──(HTTP/80)──> Frontend (Orion Nexus)           │
│  └────────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Application Layer                               │
│  ┌─────────────────┐         ┌──────────────────┐                   │
│  │  Orion Nexus    │◄──────►│  Oruga Backend   │                   │
│  │  Frontend       │         │  (FastAPI:8000)  │                   │
│  │  (React:80)     │         └──────────────────┘                   │
│  └─────────────────┘                   │                             │
│                                        │                             │
│  ┌─────────────────┐                  │                             │
│  │  ETL Service    │                  │                             │
│  │  (Flask:8080)   │                  │                             │
│  └─────────────────┘                  │                             │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FIWARE Layer                                 │
│  ┌─────────────────┐         ┌──────────────────┐                   │
│  │ Sensor Gateway  │────────►│  Orion Context   │                   │
│  │ (Flask:81)      │         │  Broker (:1026)  │                   │
│  └─────────────────┘         └──────────────────┘                   │
│         ▲                              │                             │
│         │                              ▼                             │
│    IoT Sensors              ┌──────────────────┐                    │
│  (sensor001,002)            │  Quantum Leap    │                    │
│                             │  (:8668)         │                    │
│                             └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Layer                                    │
│  ┌─────────────────┐         ┌──────────────────┐                   │
│  │   MongoDB       │         │    CrateDB       │                   │
│  │   (:27017)      │         │  (:4200,:5432)   │                   │
│  │                 │         │                  │                   │
│  │ • Orion Context │         │ • Time Series    │                   │
│  │ • ETL Curated   │         │ • Sensor Data    │                   │
│  │   Data          │         │                  │                   │
│  └─────────────────┘         └──────────────────┘                   │
│                                        │                             │
│                                        ▼                             │
│                             ┌──────────────────┐                    │
│                             │     Grafana      │                    │
│                             │     (:3000)      │                    │
│                             └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Sensor Data Ingestion
```
IoT Sensor → Sensor Gateway (validate token) → Orion Context Broker → Quantum Leap → CrateDB
```

### 2. ETL Processing
```
CrateDB (time series) → ETL Service (calculate KPIs) → MongoDB (curated data)
```

### 3. User Interface
```
User → Frontend (React) → Oruga Backend (FastAPI) → Orion Context Broker
                        ↘ ETL Service (REST API) → MongoDB
```

## Service Directory Structure

```
e:/IoT/Ambiente/
│
├── services/                           # All custom application services
│   │
│   ├── sensor-gateway/                 # Port 81 (HTTP webhook endpoint)
│   │   ├── dockerfile
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   └── src/
│   │       └── main.py                 # Token validation & Orion forwarding
│   │
│   ├── etl-service/                    # Port 8080 (REST API & schedulers)
│   │   ├── dockerfile
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   ├── app.py                      # Main Flask application
│   │   ├── configuration.py            # Database & service config
│   │   ├── scheduler.py                # Background ETL schedulers
│   │   ├── utils.py                    # Database connection utilities
│   │   ├── routes/
│   │   │   ├── gps_routes.py           # GPS REST endpoints
│   │   │   └── irrigation_routes.py    # Irrigation REST endpoints
│   │   └── services/
│   │       ├── gps_service.py          # GPS ETL logic
│   │       └── irrigation_service.py   # Irrigation KPI calculation
│   │
│   ├── oruga-backend/                  # Port 8000 (FastAPI REST API)
│   │   ├── dockerfile
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   ├── .env
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py                 # FastAPI application
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── models.py           # Pydantic models
│   │       │   └── routes_commands.py  # Command routing
│   │       └── core/
│   │           ├── __init__.py
│   │           ├── config.py           # Settings management
│   │           └── orion_client.py     # Orion API client
│   │
│   └── orion-nexus-frontend/           # Port 80 (React + nginx)
│       ├── dockerfile                  # Multi-stage build
│       ├── nginx.conf                  # nginx configuration
│       ├── README.md
│       ├── .env.example
│       ├── package.json
│       ├── vite.config.ts
│       ├── public/
│       └── src/
│           ├── App.tsx
│           ├── components/
│           │   ├── EntityCreator.tsx
│           │   ├── EntityList.tsx
│           │   └── ui/                 # shadcn/ui components
│           ├── hooks/
│           ├── lib/
│           └── pages/
│               ├── Index.tsx
│               ├── Controller.tsx
│               ├── Login.tsx
│               └── NotFound.tsx
│
├── docs/                               # Project documentation
│   ├── api/                            # API specifications
│   ├── deployment/                     # Deployment guides
│   └── sensors/                        # Sensor specifications
│
├── docker-compose.yml                  # Orchestration configuration
├── README.md                           # Main project documentation
└── ARCHITECTURE.md                     # This file

# Legacy folders (to be migrated):
# - agente/ → Moved to services/sensor-gateway/
# - proyectoapp/ → Moved to services/etl-service/
# - orion-nexus/ → Split into services/orion-nexus-frontend/ and services/oruga-backend/
```

## Services Description

### Custom Application Services

#### 1. Orion Nexus Frontend (Port 80)
**Technology:** React 18 + TypeScript + Vite + shadcn/ui  
**Container:** nginx (multi-stage build)  
**Purpose:** Web interface for managing IoT entities and visualizing data

**Key Features:**
- Entity creation and management UI
- Real-time controller dashboard
- Responsive design with modern UI components
- Proxies API calls to oruga-backend

**Dependencies:** oruga-backend

---

#### 2. Oruga Backend (Port 8000)
**Technology:** FastAPI + Python 3.11  
**Purpose:** REST API layer for Orion Context Broker commands and business logic

**Key Features:**
- NGSI-LD entity management
- Command routing for IoT devices
- Health monitoring with Orion connectivity check
- OpenAPI/Swagger documentation at `/docs`

**Dependencies:** orion

---

#### 3. ETL Service (Port 8080)
**Technology:** Flask + Python 3.10  
**Purpose:** Extract-Transform-Load pipeline for sensor data analytics

**Key Features:**
- **Irrigation Service** (every 5 min):
  - Calculates irrigation KPI from temperature/humidity
  - 5 action levels: no_irrigation → maximum_irrigation
  - Adjusts recommendations based on humidity thresholds
  
- **GPS Service** (every 1 min):
  - Stores location history with GeoJSON format
  - Tracks device movement over time

**REST API Endpoints:**
- `GET /irrigation` - Latest KPI
- `GET /irrigation/historial` - KPI history
- `POST /irrigation/run-etl` - Manual ETL trigger
- `GET /gps` - Latest location
- `GET /gps/historial` - Location history
- `POST /gps/run-etl` - Manual ETL trigger

**Dependencies:** mongo-db, crate-db

---

#### 4. Sensor Gateway (Port 81)
**Technology:** Flask + Python 3.10  
**Purpose:** Secure entry point for IoT sensor data

**Key Features:**
- Token-based authentication (`"token": "secreto"`)
- Dynamic sensor routing: `/recibirdatos/<sensor_id>`
- Forwards validated data to Orion via PATCH
- Returns 401 for invalid tokens

**Supported Sensors:**
- **sensor001**: Temperature (°C) & Humidity (%)
- **sensor002**: GPS coordinates (lat/lon)

**Dependencies:** orion

---

### FIWARE Components

#### Orion Context Broker (Port 1026)
**Image:** fiware/orion-ld  
**Purpose:** NGSI-LD compliant context information management

Stores current state of all IoT entities and propagates updates to subscribers (Quantum Leap).

---

#### Quantum Leap (Port 8668)
**Image:** orchestracities/quantumleap  
**Purpose:** Time-series data persistence

Subscribes to Orion entity changes and stores historical data in CrateDB.

---

### Databases

#### MongoDB (Port 27017)
**Image:** mongo:3.6  
**Purpose:** 
1. Orion Context Broker backend (current entity states)
2. ETL Service curated data storage

**Collections:**
- `sprinkler_db.riego_kpi` - Irrigation recommendations
- `gps_db.location_history` - GPS tracking history

---

#### CrateDB (Ports 4200, 4300, 5432)
**Image:** crate  
**Purpose:** Time-series database for sensor telemetry

**Tables:**
- `etsensortemphum` - Temperature & humidity readings (sensor001)
- `etsensorgps` - GPS coordinates (sensor002)

**Interfaces:**
- 4200: Admin UI
- 4300: Transport protocol
- 5432: PostgreSQL wire protocol

---

#### Grafana (Port 3000)
**Image:** grafana/grafana  
**Purpose:** Data visualization and dashboards

Can query both CrateDB (time series) and MongoDB (curated data).

**Credentials:** admin/admin

---

## Port Map

| Port | Service | Protocol | Description |
|------|---------|----------|-------------|
| 80 | orion-nexus-frontend | HTTP | Web UI |
| 81 | sensor-gateway | HTTP | Sensor webhook endpoint |
| 1026 | orion | HTTP | NGSI-LD API |
| 3000 | grafana | HTTP | Visualization dashboard |
| 4200 | crate-db | HTTP | CrateDB Admin UI |
| 4300 | crate-db | Binary | CrateDB transport |
| 5432 | crate-db | PostgreSQL | CrateDB SQL interface |
| 8000 | oruga-backend | HTTP | FastAPI REST API |
| 8080 | etl-service | HTTP | ETL REST API |
| 8668 | quantumleap | HTTP | Time-series API |
| 27017 | mongo-db | MongoDB | Database |

## Network Configuration

All services run on a custom Docker network:
```yaml
networks:
  default:
    ipam:
      config:
        - subnet: 172.19.1.0/24
```

Services communicate using Docker DNS (e.g., `http://orion:1026`).

## Environment Variables

### Oruga Backend
Located in `services/oruga-backend/.env`:
```bash
APP_NAME=Oruga Backend
API_PREFIX=/api/v1
ORION_HOST=http://orion:1026
```

### Frontend
Located in `services/orion-nexus-frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_ORION_URL=http://localhost:1026
```

### ETL Service
Configured in `services/etl-service/configuration.py`:
- CrateDB: `http://crate-db:4200`
- MongoDB: `mongodb://mongo-db:27017/`

## Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2+
- 8GB RAM recommended
- Linux: `sudo sysctl -w vm.max_map_count=262144` (for CrateDB)

### Start All Services
```powershell
cd e:\IoT\Ambiente
docker compose up --build -d
```

### Check Service Health
```powershell
docker compose ps
docker compose logs -f <service-name>
```

### Stop All Services
```powershell
docker compose down
```

### Clean Restart (delete volumes)
```powershell
docker compose down -v
docker compose up --build -d
```

## Migration Guide

If you have the old folder structure (`agente/`, `proyectoapp/`, `orion-nexus/`), follow these steps:

1. **Copy files to new structure:**
   ```powershell
   # Sensor Gateway
   Copy-Item -Recurse .\agente\* .\services\sensor-gateway\
   
   # ETL Service
   Copy-Item -Recurse .\proyectoapp\* .\services\etl-service\
   
   # Oruga Backend
   Copy-Item -Recurse .\orion-nexus\backend\* .\services\oruga-backend\
   
   # Frontend
   Copy-Item -Recurse .\orion-nexus\* .\services\orion-nexus-frontend\
   Remove-Item .\services\orion-nexus-frontend\backend -Recurse
   ```

2. **Update docker-compose.yml** to use new `./services/` paths (already done in provided file)

3. **Test the deployment:**
   ```powershell
   docker compose up --build
   ```

4. **Once verified, remove old folders:**
   ```powershell
   Remove-Item -Recurse .\agente, .\proyectoapp, .\orion-nexus
   ```

## Development Workflow

### Frontend Development
```bash
cd services/orion-nexus-frontend
npm install
npm run dev
# Access at http://localhost:5173
```

### Backend Development
```bash
cd services/oruga-backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Access at http://localhost:8000/docs
```

### ETL Service Development
```bash
cd services/etl-service
pip install -r requirements.txt
python3 app.py
# Access at http://localhost:8080
```

## Monitoring & Debugging

### View Logs
```powershell
# All services
docker compose logs -f

# Specific service
docker compose logs -f orion-nexus-frontend
docker compose logs -f oruga-backend
docker compose logs -f etl-service
docker compose logs -f sensor-gateway
```

### Database Access

**MongoDB:**
```powershell
docker exec -it db-mongo mongo
```

**CrateDB:**
Open browser: http://localhost:4200

**Grafana:**
Open browser: http://localhost:3000 (admin/admin)

### Health Checks
- Frontend: http://localhost:80/health
- Backend: http://localhost:8000/health
- ETL: http://localhost:8080/
- Orion: http://localhost:1026/version
- CrateDB: http://localhost:4200

## Security Considerations

1. **Sensor Gateway**: Change default token from `"secreto"` to a strong secret
2. **Grafana**: Change default admin password
3. **MongoDB**: Enable authentication for production
4. **CrateDB**: Enable authentication (`-Cauth.host_based.enabled=true`)
5. **Network**: Restrict external access to only necessary ports (80, 3000)

## Scalability

To scale individual services:

```powershell
docker compose up -d --scale sensor-gateway=3
```

For production, consider:
- Load balancer in front of frontend/backend
- Separate MongoDB replica set
- CrateDB cluster with multiple nodes
- Redis for ETL job queuing
- Message broker (RabbitMQ/MQTT) for sensor ingestion

## Troubleshooting

### Service won't start
Check dependencies are healthy:
```powershell
docker compose ps
docker compose logs <service-name>
```

### CrateDB memory issues
Adjust heap size in docker-compose.yml:
```yaml
environment:
  - CRATE_HEAP_SIZE=2g  # Reduce if needed
```

### Frontend can't reach backend
Check nginx proxy configuration in `services/orion-nexus-frontend/nginx.conf`

### ETL not processing data
1. Verify CrateDB tables exist and have data
2. Check MongoDB connectivity
3. Review ETL logs for errors

## Contributing

When adding new services:
1. Create folder in `services/<service-name>/`
2. Include dockerfile, README.md, requirements.txt
3. Update docker-compose.yml
4. Document in this file
5. Add to main README.md

## License

[Specify your license here]

## Contact

[Add contact information or repository link]
