# Smart Irrigation & GPS Monitoring Platform

## Overview
This project deploys a small FIWARE-based stack that ingests telemetry from two field sensors, processes it through custom ETL services, and exposes the latest KPIs and location history over a REST API. The stack is composed of two first-party services plus core FIWARE components orchestrated with Docker Compose:

- **`agente`** – lightweight Flask gateway that authenticates incoming sensor payloads and forwards them to Orion Context Broker.
- **`proyectoapp`** – Unified ETL Flask app that reads contextual data from CrateDB (populated by Orion/Quantum Leap), calculates irrigation KPIs, stores curated results in MongoDB, and publishes REST endpoints for dashboards or client apps.
- **FIWARE services** – Orion Context Broker, Quantum Leap, CrateDB, MongoDB, and Grafana complete the end-to-end pipeline.

<p align="center">
Data Flow: Sensor → `agente` (token validation) → Orion → Quantum Leap → CrateDB → `proyectoapp` ETL → MongoDB → REST API / Grafana.
</p>

## Architecture

### Container Topology
The `docker-compose.yml` file defines the following services:

| Service | Description | Key Ports |
| --- | --- | --- |
| `agente` | Receives sensor webhooks on port 80, validates payloads, and issues PATCH updates to Orion entities. | 80 |
| `etl` (`proyectoapp`) | Flask REST API and ETL schedulers running on port 8080. | 8080 |
| `orion` | FIWARE Orion-LD context broker providing NGSI-LD APIs. | 1026 |
| `quantumleap` | Time-series bridge that persists context changes into CrateDB. | 8668 |
| `mongo-db` | MongoDB instance used as curated store for ETL outputs. | 27017 |
| `crate-db` | CrateDB cluster node storing raw sensor time series. | 4200, 4300, 5432 |
| `grafana` | Visualization layer connected to CrateDB or MongoDB. | 3000 |

All containers share the same Docker network (`172.19.1.0/24`) to enable service discovery by hostname (e.g., `http://orion:1026`).

### Data Journey
1. **Field sensors** call the public webhook exposed by `agente`.
2. `agente` verifies the shared secret token, removes it from the payload, and forwards the remaining attributes to Orion via NGSIv2 PATCH (`/v2/entities/{sensor}/attrs`).
3. Orion propagates the attribute changes to Quantum Leap, which appends them to the appropriate CrateDB time-series tables (`etsensortemphum`, `etsensorgps`).
4. `proyectoapp` periodically extracts the freshest records from CrateDB:
   - Calculates a human-friendly irrigation KPI from temperature and humidity.
   - Stores both KPI and GPS breadcrumbs in MongoDB collections.
5. `proyectoapp` exposes REST endpoints that serve the latest KPI/location as well as paginated history. Grafana can query MongoDB directly or CrateDB for visualization.

### Scheduling
Background ETL loops are started when `proyectoapp/app.py` runs:

- **Irrigation ETL** (`etl_process_irrigation`) – every 5 minutes.
- **GPS ETL** (`etl_process_gps`) – every minute.

Manual execution is available through POST endpoints (see below).

## Sensor Ingestion Contracts

Two sensor IDs are currently supported, each with its own telemetry schema. Both routes require an HTTP `POST` with `Content-Type: application/json` (or any body with a parseable JSON) and must include the shared token `"secreto"`.

### Sensor 001 – Temperature & Humidity
- **Endpoint:** `http://localhost/recibirdatos/sensor001`
- **Payload schema:**

```json
{
  "temperatura": { "type": "float", "value": 22.65 },
  "humedad": { "type": "float", "value": 60.5 },
  "token": "secreto"
}
```

Upon validation, `agente` forwards `{temperatura, humedad}` to Orion entity `sensor001`. The ETL service later reads from CrateDB table `etsensortemphum` and computes an irrigation KPI based on temperature bands and humidity adjustments.

### Sensor 002 – GPS Tracker
- **Endpoint:** `http://localhost/recibirdatos/sensor002`
- **Payload schema:**

```json
{
  "latitud": { "type": "float", "value": 6.26195 },
  "longitud": { "type": "float", "value": -75.59046 },
  "token": "secreto"
}
```

After validation, the gateway patches Orion entity `sensor002`. Quantum Leap records the stream in CrateDB (`etsensorgps`), and the ETL app stores each point in MongoDB using GeoJSON (`{"type": "Point", "coordinates": [lon, lat]}`).

> ❗ **Token validation**: Requests without the token or with an incorrect value return `401 Token de autenticacion incorrecto` and nothing is pushed to Orion.

### Testing the Webhooks (PowerShell example)

```powershell
Invoke-RestMethod -Uri "http://localhost/recibirdatos/sensor001" -Method Post -Body '{
  "temperatura": { "type": "float", "value": 23.1 },
  "humedad": { "type": "float", "value": 58.0 },
  "token": "secreto"
}' -ContentType 'application/json'
```

## ETL Service API (`proyectoapp`)

The Flask API listens on port **8080**. All routes return JSON.

### Root
- `GET /` – Health message plus hyperlinks to the irrigation and GPS modules.

### Irrigation module (`routes/irrigation_routes.py`)
- `GET /irrigation` – Latest KPI document from MongoDB (`sprinkler_db.riego_kpi`).
- `GET /irrigation/historial?limit=10` – Most recent KPI records (default limit 10).
- `POST /irrigation/run-etl` – Triggers `etl_process_irrigation()` immediately.

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

### GPS module (`routes/gps_routes.py`)
- `GET /gps` – Latest GPS fix from MongoDB (`gps_db.location_history`).
- `GET /gps/historial?limit=10` – Latest GPS points (default limit 10).
- `POST /gps/run-etl` – Triggers `etl_process_gps()` immediately.

Example document:
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

## Deployment & Operations

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2
- Open TCP ports: `80`, `8080`, `1026`, `8668`, `27017`, `4200`, `4300`, `5432`, `3000`

### First-time Setup
1. Clone or copy the workspace contents onto the target host.
2. Build and launch all services:

```powershell
cd e:\IoT\Ambiente
docker compose up --build
```

3. Wait for the health checks (`mongo-db`, `crate-db`, `orion`) to report healthy. The ETL app will log when databases are reachable and when schedulers start.

4. Point sensors (or testing scripts) to the public IP/hostname exposing port 80 for the webhook gateway.

### Day-to-day Operations
- **Manual ETL runs:** issue `POST` to `/irrigation/run-etl` or `/gps/run-etl`.
- **Log inspection:**
  - `docker compose logs agente -f`
  - `docker compose logs etl -f`
- **Database connections:**
  - MongoDB shell: `mongodb://localhost:27017`
  - CrateDB console: `http://localhost:4200`
- **Grafana UI:** `http://localhost:3000` (default admin/admin credentials).

### Stopping the Stack

```powershell
docker compose down
```

Add `-v` to also drop MongoDB/CrateDB/Grafana volumes if you need a clean slate.

## Project Structure

```
.
├── docker-compose.yml
├── agente/
│   ├── dockerfile
│   ├── requirements.txt
│   └── src/
│       └── main.py
└── proyectoapp/
    ├── app.py
    ├── configuration.py
    ├── dockerfile
    ├── requirements.txt
    ├── scheduler.py
    ├── utils.py
    ├── routes/
    │   ├── gps_routes.py
    │   └── irrigation_routes.py
    └── services/
        ├── gps_service.py
        └── irrigation_service.py
```

### Key Dependencies
- Flask (REST API server)
- Requests (HTTP forwarding to Orion)
- PyMongo (MongoDB client)
- CrateDB Python client
- Schedule (lightweight scheduler for ETL loops)

## Extending the Platform
- **New sensors:** add new routes in `agente` (if token or validation differs) and extend `proyectoapp/services` with corresponding ETL logic and MongoDB collections.
- **Authentication:** replace shared token with per-sensor keys or OAuth 2.0 reverse proxy if needed.
- **Alerting:** hook Grafana alerts or send notifications from ETL processes when KPIs exceed thresholds.

---

### Quick Reference
- Sensor webhooks: `http://localhost/recibirdatos/<sensor_id>` (token required).
- ETL API base URL: `http://localhost:8080` (inside Docker host).
- MongoDB curated collections: `sprinkler_db.riego_kpi`, `gps_db.location_history`.
- CrateDB raw tables: `etsensortemphum`, `etsensorgps`.

Happy monitoring!
