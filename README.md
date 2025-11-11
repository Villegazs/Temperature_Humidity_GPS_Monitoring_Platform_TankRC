# Temperature, Humidity & GPS Monitoring Platform

## Overview
Complete FIWARE-based IoT platform for smart irrigation and GPS tracking. This project deploys a modular microservices architecture that ingests telemetry from field sensors, processes data through intelligent ETL pipelines, and provides both REST APIs and a modern web interface for monitoring and control.

### System C## Key Technologies

- **Frontend**: React 18, TypeScript, Vite, shadcn/ui, TailwindCSS
- **Backend**: FastAPI, Python 3.11, Pydantic, Uvicorn
- **ETL**: Flask, Python 3.10, Schedule, PyMongo, CrateDB client
- **FIWARE**: Orion Context Broker (NGSI-LD), Quantum Leap
- **Databases**: MongoDB 3.6, CrateDB, PostgreSQL wire protocol
- **Visualization**: Grafana
- **Infrastructure**: Docker, Docker Compose, nginx

## Quick Reference

| Component | URL | Credentials |
|-----------|-----|-------------|
| Web UI | http://localhost | - |
| Backend API Docs | http://localhost:8000/docs | - |
| ETL API | http://localhost:8080 | - |
| Sensor Webhook | http://98.91.29.98/recibirdatos/`<sensor_id>` | token: secreto |
| Orion Context Broker | http://localhost:1026 | - |
| Grafana | http://localhost:3000 | admin/admin |
| CrateDB UI | http://localhost:4200 | - |
| MongoDB | mongodb://localhost:27017 | - |

**Database Collections:**
- `sprinkler_db.riego_kpi` - Irrigation KPIs (MongoDB)
- `gps_db.location_history` - GPS tracking (MongoDB)
- `etsensortemphum` - Temperature/Humidity (CrateDB)
- `etsensorgps` - GPS coordinates (CrateDB)

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture and data flows
- **[services/sensor-gateway/README.md](./services/sensor-gateway/README.md)** - Sensor webhook gateway
- **[services/etl-service/README.md](./services/etl-service/README.md)** - ETL processing logic
- **[services/oruga-backend/README.md](./services/oruga-backend/README.md)** - FastAPI backend
- **[services/orion-nexus-frontend/README.md](./services/orion-nexus-frontend/README.md)** - React frontend

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-sensor`)
3. Commit changes (`git commit -am 'Add new sensor support'`)
4. Push to branch (`git push origin feature/new-sensor`)
5. Create Pull Request

## License

[Specify your license]

## Support

For issues and questions:
- GitHub Issues: [Repository Link]
- Documentation: See `docs/` folder
- Architecture: See ARCHITECTURE.md

---

**Built with ❤️ using FIWARE IoT Stack**

**Custom Application Services:**
- **Frontend (Orion Nexus)** – React + TypeScript web interface with shadcn/ui components (Port 80)
- **Backend API (Oruga)** – FastAPI service for Orion command management (Port 8000)
- **ETL Service** – Automated data processing with irrigation KPI calculation (Port 8080)
- **Sensor Gateway** – Secure webhook endpoint for IoT data ingestion (Port 81)

**FIWARE & Infrastructure:**
- **Orion Context Broker** – NGSI-LD entity management (Port 1026)
- **Quantum Leap** – Time-series data persistence (Port 8668)
- **CrateDB** – Sensor telemetry storage (Port 4200)
- **MongoDB** – Curated data & context storage (Port 27017)
- **Grafana** – Visualization dashboards (Port 3000)

### Data Flow
```
IoT Sensors → Sensor Gateway (validate) → Orion → Quantum Leap → CrateDB
                                           ↓
                                        Oruga Backend ← Frontend (User)
                                           
CrateDB → ETL Service (KPI calculation) → MongoDB → REST API → Frontend/Grafana
```

📖 **For detailed architecture, see [ARCHITECTURE.md](./ARCHITECTURE.md)**

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2+
- 8GB RAM recommended
- Ports available: 80, 81, 1026, 3000, 4200, 8000, 8080, 8668, 27017

### Linux Additional Setup
```bash
sudo sysctl -w vm.max_map_count=262144
```

### Deploy All Services
```powershell
# Clone repository
cd e:\IoT\Ambiente

# Start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Access Points
- **Web UI**: http://localhost (Orion Nexus Frontend)
- **Backend API**: http://localhost:8000/docs (FastAPI Swagger)
- **ETL API**: http://localhost:8080 (Flask REST)
- **Sensor Webhook**: http://localhost:81/recibirdatos/<sensor_id>
- **Orion Context Broker**: http://localhost:1026/version
- **Grafana**: http://localhost:3000 (admin/admin)
- **CrateDB Console**: http://localhost:4200

### Stop Services
```powershell
docker compose down

# With volume cleanup
docker compose down -v
```

## Project Structure

```
e:/IoT/Ambiente/
├── services/                      # All custom application services
│   ├── orion-nexus-frontend/     # React web interface (Port 80)
│   ├── oruga-backend/            # FastAPI backend (Port 8000)
│   ├── etl-service/              # Data processing (Port 8080)
│   └── sensor-gateway/           # IoT ingestion (Port 81)
├── docs/                          # Documentation
├── docker-compose.yml            # Service orchestration
├── README.md                     # This file
└── ARCHITECTURE.md               # Detailed architecture guide
```

Each service has its own README with specific documentation.

## Service Responsibilities

### 1. Sensor Gateway (`services/sensor-gateway/`)
- **Port**: 81
- **Tech**: Flask + Python 3.10
- **Purpose**: Secure webhook endpoint for IoT sensors
- Validates authentication tokens
- Forwards data to Orion Context Broker
- Supports dynamic sensor routing

### 2. ETL Service (`services/etl-service/`)
- **Port**: 8080
- **Tech**: Flask + Python 3.10
- **Purpose**: Data processing and KPI calculation
- **Irrigation ETL** (every 5 min): Calculates irrigation recommendations
- **GPS ETL** (every 1 min): Stores location history
- Exposes REST API for querying processed data

### 3. Oruga Backend (`services/oruga-backend/`)
- **Port**: 8000
- **Tech**: FastAPI + Python 3.11
- **Purpose**: Backend API for frontend operations
- Manages Orion entities and commands
- Provides health checks and monitoring
- OpenAPI documentation at `/docs`

### 4. Orion Nexus Frontend (`services/orion-nexus-frontend/`)
- **Port**: 80
- **Tech**: React 18 + TypeScript + Vite
- **Purpose**: Web interface for users
- Entity management UI
- Real-time controller dashboard
- Responsive modern design with shadcn/ui

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed component interactions.

## Sensor Integration

### Supported Sensors

The platform supports two IoT sensors sending data via HTTP POST to the Sensor Gateway.

#### Sensor 001 – Temperature & Humidity
Monitors environmental conditions for irrigation decision-making.

**Endpoint:** `http://98.91.29.98/recibirdatos/sensor001` (or `http://localhost:81/recibirdatos/sensor001` in local Docker)

**Payload:**
```json
{
  "temperatura": { "type": "float", "value": 22.65 },
  "humedad": { "type": "float", "value": 60.5 },
  "token": "secreto"
}
```

**Data Flow:**
1. Gateway validates token → forwards to Orion entity `sensor001`
2. Quantum Leap stores in CrateDB table `etsensortemphum`
3. ETL Service calculates irrigation KPI every 5 minutes
4. Results stored in MongoDB collection `sprinkler_db.riego_kpi`

**Irrigation KPI Levels:**
- Level 0: No irrigation (< 15°C)
- Level 1: Minimum irrigation (15-20°C)
- Level 2: Normal irrigation (20-25°C)
- Level 3: Intense irrigation (25-30°C)
- Level 4: Maximum irrigation (> 30°C)
- *Adjusted ±1 level based on humidity thresholds*

#### Sensor 002 – GPS Tracker
Tracks device location for movement monitoring.

**Endpoint:** `http://98.91.29.98/recibirdatos/sensor002` (or `http://localhost:81/recibirdatos/sensor002` in local Docker)

**Payload:**
```json
{
  "latitud": { "type": "float", "value": 6.26195 },
  "longitud": { "type": "float", "value": -75.59046 },
  "token": "secreto"
}
```

**Data Flow:**
1. Gateway validates token → forwards to Orion entity `sensor002`
2. Quantum Leap stores in CrateDB table `etsensorgps`
3. ETL Service processes every 1 minute
4. Location stored in MongoDB collection `gps_db.location_history` (GeoJSON format)

### Security
> ⚠️ **Authentication Required**: All sensor requests must include `"token": "secreto"`. Invalid or missing tokens return `401 Unauthorized`.

### Testing Sensor Endpoints

**PowerShell:**
```powershell
# Test Temperature/Humidity Sensor
Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor001" `
  -Method Post `
  -Body '{"temperatura":{"type":"float","value":23.5},"humedad":{"type":"float","value":58.0},"token":"secreto"}' `
  -ContentType 'application/json'

# Test GPS Sensor
Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor002" `
  -Method Post `
  -Body '{"latitud":{"type":"float","value":6.26195},"longitud":{"type":"float","value":-75.59046},"token":"secreto"}' `
  -ContentType 'application/json'
```

**curl (Linux/Mac):**
```bash
# Temperature/Humidity
curl -X POST http://localhost:81/recibirdatos/sensor001 \
  -H "Content-Type: application/json" \
  -d '{"temperatura":{"type":"float","value":23.5},"humedad":{"type":"float","value":58.0},"token":"secreto"}'

# GPS
curl -X POST http://localhost:81/recibirdatos/sensor002 \
  -H "Content-Type: application/json" \
  -d '{"latitud":{"type":"float","value":6.26195},"longitud":{"type":"float","value":-75.59046},"token":"secreto"}'
```

## REST API Endpoints

### ETL Service API (Port 8080)

All routes return JSON.

#### Root
- `GET /` – Service health and available endpoints

#### Irrigation Module
- `GET /irrigation` – Latest KPI document
- `GET /irrigation/historial?limit=10` – KPI history (default 10 records)
- `POST /irrigation/run-etl` – Manual ETL trigger

Documents contain:
```json
{
  "timestamp": "2025-10-27T14:35:02.123456",
  "sensor_time_index": "2025-10-27T14:34:00.000000Z",
  "temperature": 23.5,
  "humidity": 55.0,
  "kpi": {
    "action": "normal_irrigation",
    "level": 2,
    "description": "Temperatura normal (23.5°C), humedad normal (55.0%)"
  }
}
```

#### GPS Module
- `GET /gps` – Latest GPS location
- `GET /gps/historial?limit=10` – Location history (default 10 records)
- `POST /gps/run-etl` – Manual ETL trigger

GPS documents (GeoJSON format):
```json
{
  "timestamp": "2025-10-27T14:35:06.123456",
  "sensor_time_index": "2025-10-27T14:35:00.000000Z",
  "location": {
    "type": "Point",
    "coordinates": [-75.59046, 6.26195]
  }
}
```

### Oruga Backend API (Port 8000)

FastAPI service with OpenAPI documentation.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: `GET /health`

See interactive documentation for full endpoint list.

## Operations

### Monitoring

**View Service Logs:**
```powershell
# All services
docker compose logs -f

# Specific services
docker compose logs -f orion-nexus-frontend
docker compose logs -f oruga-backend
docker compose logs -f etl-service
docker compose logs -f sensor-gateway
```

**Check Service Health:**
```powershell
docker compose ps
```

**Manual ETL Execution:**
```powershell
# Irrigation ETL
Invoke-RestMethod -Uri "http://localhost:8080/irrigation/run-etl" -Method Post

# GPS ETL
Invoke-RestMethod -Uri "http://localhost:8080/gps/run-etl" -Method Post
```

### Database Access

**MongoDB Shell:**
```powershell
docker exec -it db-mongo mongo
```

**CrateDB Console:**  
http://localhost:4200

**Grafana Dashboard:**  
http://localhost:3000 (admin/admin)

### Backup & Restore

**Export MongoDB Data:**
```powershell
docker exec db-mongo mongodump --archive=/data/backup.archive
docker cp db-mongo:/data/backup.archive ./backup.archive
```

**Restore MongoDB Data:**
```powershell
docker cp ./backup.archive db-mongo:/data/backup.archive
docker exec db-mongo mongorestore --archive=/data/backup.archive
```

## Development

### Local Service Development

**Frontend:**
```bash
cd services/orion-nexus-frontend
npm install
npm run dev  # http://localhost:5173
```

**Backend:**
```bash
cd services/oruga-backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

**ETL Service:**
```bash
cd services/etl-service
pip install -r requirements.txt
python app.py  # http://localhost:8080
```

See individual service READMEs for more details.

## Extending the Platform

### Adding New Sensors
1. Update `services/sensor-gateway/src/main.py` if special validation needed
2. Create new service in `services/etl-service/services/`
3. Add routes in `services/etl-service/routes/`
4. Update scheduler in `services/etl-service/scheduler.py`
5. Document sensor payload in this README

### Customization Ideas
- **Authentication**: Replace shared token with JWT or API keys
- **Alerting**: Integrate with SMS/email for KPI threshold alerts
- **ML Models**: Add predictive irrigation based on weather forecasts
- **Mobile App**: Build native app consuming REST APIs
- **Real-time Dashboard**: WebSocket updates for live monitoring

## Troubleshooting

### Frontend Not Loading
- Check nginx logs: `docker compose logs orion-nexus-frontend`
- Verify backend is running: `curl http://localhost:8000/health`

### ETL Not Processing
- Verify CrateDB has data: http://localhost:4200
- Check MongoDB connection: `docker exec -it db-mongo mongo`
- Review ETL logs: `docker compose logs etl-service`

### Sensor Data Not Appearing
1. Test sensor endpoint: Use curl/PowerShell examples above
2. Check Orion Context Broker: `curl http://localhost:1026/v2/entities`
3. Verify Quantum Leap: `curl http://localhost:8668/version`
4. Inspect CrateDB tables: `SELECT * FROM etsensortemphum LIMIT 5`

---

### Quick Reference
- Sensor webhooks: `http://localhost/recibirdatos/<sensor_id>` (token required).
- ETL API base URL: `http://localhost:8080` (inside Docker host).
- MongoDB curated collections: `sprinkler_db.riego_kpi`, `gps_db.location_history`.
- CrateDB raw tables: `etsensortemphum`, `etsensorgps`.

Happy monitoring!
