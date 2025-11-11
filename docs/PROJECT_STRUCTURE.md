# Project Structure Reference

## Complete Directory Tree

```
e:/IoT/Ambiente/
│
├── 📄 README.md                          # Main project documentation
├── 📄 ARCHITECTURE.md                    # Detailed system architecture
├── 📄 docker-compose.yml                # Service orchestration
├── 📄 .gitmodules                        # Git submodules (if any)
├── 🔧 migrate-structure.ps1             # Migration helper script
│
├── 📁 services/                          # All custom application services
│   │
│   ├── 📁 sensor-gateway/               # Port 81 - IoT Data Ingestion
│   │   ├── 📄 dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📄 README.md
│   │   └── 📁 src/
│   │       └── 📄 main.py               # Flask webhook server
│   │
│   ├── 📁 etl-service/                  # Port 8080 - Data Processing
│   │   ├── 📄 dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📄 README.md
│   │   ├── 📄 app.py                    # Main Flask app
│   │   ├── 📄 configuration.py          # Config settings
│   │   ├── 📄 scheduler.py              # Background schedulers
│   │   ├── 📄 utils.py                  # Database utilities
│   │   ├── 📁 routes/
│   │   │   ├── 📄 gps_routes.py         # GPS REST endpoints
│   │   │   └── 📄 irrigation_routes.py  # Irrigation REST endpoints
│   │   └── 📁 services/
│   │       ├── 📄 gps_service.py        # GPS ETL logic
│   │       └── 📄 irrigation_service.py # Irrigation KPI calculation
│   │
│   ├── 📁 oruga-backend/                # Port 8000 - FastAPI Backend
│   │   ├── 📄 dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📄 README.md
│   │   ├── 📄 .env                      # Environment variables
│   │   └── 📁 app/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 main.py               # FastAPI application
│   │       ├── 📁 api/
│   │       │   ├── 📄 __init__.py
│   │       │   ├── 📄 models.py         # Pydantic models
│   │       │   └── 📄 routes_commands.py # Command routing
│   │       └── 📁 core/
│   │           ├── 📄 __init__.py
│   │           ├── 📄 config.py         # Settings
│   │           └── 📄 orion_client.py   # Orion API client
│   │
│   └── 📁 orion-nexus-frontend/         # Port 80 - React Web UI
│       ├── 📄 dockerfile                # Multi-stage build (node + nginx)
│       ├── 📄 nginx.conf                # nginx server config
│       ├── 📄 README.md
│       ├── 📄 .env.example
│       ├── 📄 package.json
│       ├── 📄 vite.config.ts
│       ├── 📄 tsconfig.json
│       ├── 📄 tailwind.config.ts
│       ├── 📄 components.json           # shadcn/ui config
│       ├── 📄 index.html
│       ├── 📁 public/
│       │   ├── favicon.ico
│       │   └── ...
│       └── 📁 src/
│           ├── 📄 App.tsx               # Main React component
│           ├── 📄 main.tsx
│           ├── 📄 index.css
│           ├── 📁 components/
│           │   ├── 📄 EntityCreator.tsx
│           │   ├── 📄 EntityList.tsx
│           │   └── 📁 ui/               # shadcn/ui components
│           │       ├── 📄 button.tsx
│           │       ├── 📄 card.tsx
│           │       └── ... (50+ components)
│           ├── 📁 pages/
│           │   ├── 📄 Index.tsx
│           │   ├── 📄 Controller.tsx
│           │   ├── 📄 Login.tsx
│           │   └── 📄 NotFound.tsx
│           ├── 📁 hooks/
│           │   └── 📄 use-mobile.tsx
│           └── 📁 lib/
│               └── 📄 utils.ts
│
├── 📁 docs/                              # Documentation
│   ├── 📁 api/                          # API specifications
│   ├── 📁 deployment/
│   │   └── 📄 MIGRATION_GUIDE.md        # Migration instructions
│   └── 📁 sensors/                       # Sensor specifications
│
└── 📁 [FIWARE Components]                # Managed by Docker Compose
    ├── orion (fiware/orion-ld)          # Port 1026
    ├── quantumleap                       # Port 8668
    ├── mongo-db                          # Port 27017
    ├── crate-db                          # Ports 4200, 4300, 5432
    └── grafana                           # Port 3000
```

## Service Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│                                                                   │
│  Browser ──(HTTP:80)──> orion-nexus-frontend (React + nginx)    │
│                                 │                                 │
│                                 ↓                                 │
│                          (API Calls)                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│                                                                   │
│  ┌──────────────────────┐     ┌───────────────────────┐         │
│  │  oruga-backend       │────→│  Orion Context Broker │         │
│  │  (FastAPI:8000)      │     │  (NGSI-LD:1026)       │         │
│  └──────────────────────┘     └───────────────────────┘         │
│           │                              │                        │
│           │                              ↓                        │
│           │                    ┌──────────────────┐             │
│           │                    │  Quantum Leap    │             │
│           │                    │  (:8668)         │             │
│           │                    └──────────────────┘             │
│           │                              │                        │
│           ↓                              ↓                        │
│  ┌──────────────────────┐     ┌──────────────────┐             │
│  │  etl-service         │────→│  CrateDB         │             │
│  │  (Flask:8080)        │     │  (:4200)         │             │
│  └──────────────────────┘     └──────────────────┘             │
│           │                                                       │
│           ↓                                                       │
│  ┌──────────────────────┐                                       │
│  │  MongoDB             │                                       │
│  │  (:27017)            │                                       │
│  └──────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
                                 ↑
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                      Ingestion Layer                             │
│                                                                   │
│  IoT Sensors ──(HTTP:81)──> sensor-gateway ──> Orion            │
│  (sensor001, sensor002)      (Flask)                             │
└─────────────────────────────────────────────────────────────────┘
```

## File Purpose Guide

### Configuration Files

| File | Purpose | Service |
|------|---------|---------|
| `docker-compose.yml` | Orchestrates all containers | All |
| `dockerfile` | Container build instructions | Each service |
| `requirements.txt` | Python dependencies | Python services |
| `package.json` | Node.js dependencies | Frontend |
| `.env` | Environment variables | Oruga Backend |
| `nginx.conf` | Web server config | Frontend |
| `vite.config.ts` | Build tool config | Frontend |
| `configuration.py` | App settings | ETL Service |

### Application Files

| File | Purpose | Service |
|------|---------|---------|
| `main.py` | Entry point | Sensor Gateway, Oruga Backend |
| `app.py` | Flask application | ETL Service |
| `App.tsx` | React root component | Frontend |
| `routes/*.py` | REST API endpoints | ETL Service |
| `services/*.py` | Business logic | ETL Service |
| `scheduler.py` | Background tasks | ETL Service |
| `utils.py` | Helper functions | ETL Service |

### Frontend Structure

| Directory | Purpose |
|-----------|---------|
| `src/components/` | Reusable React components |
| `src/components/ui/` | shadcn/ui component library |
| `src/pages/` | Route page components |
| `src/hooks/` | Custom React hooks |
| `src/lib/` | Utility functions |
| `public/` | Static assets (favicon, images) |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` (root) | Main project documentation |
| `ARCHITECTURE.md` | System architecture details |
| `services/*/README.md` | Service-specific docs |
| `docs/deployment/MIGRATION_GUIDE.md` | Migration instructions |

## Quick Navigation

### Working with Frontend
```bash
cd services/orion-nexus-frontend
npm install
npm run dev
```

### Working with Backend
```bash
cd services/oruga-backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Working with ETL
```bash
cd services/etl-service
pip install -r requirements.txt
python app.py
```

### Working with Sensor Gateway
```bash
cd services/sensor-gateway
pip install -r requirements.txt
python src/main.py
```

### Viewing Logs
```powershell
# All services
docker compose logs -f

# Specific service
docker compose logs -f orion-nexus-frontend
docker compose logs -f oruga-backend
docker compose logs -f etl-service
docker compose logs -f sensor-gateway
```

### Accessing Databases
```powershell
# MongoDB
docker exec -it db-mongo mongo

# CrateDB UI
Start-Process "http://localhost:4200"
```

## Color Legend

- 📄 **File**: Individual file
- 📁 **Folder**: Directory containing multiple files
- 🔧 **Script**: Executable script
- 🐳 **Container**: Docker service

## Size Reference

Typical service sizes (after build):
- **sensor-gateway**: ~150 MB (Python + Flask)
- **etl-service**: ~200 MB (Python + Flask + DB clients)
- **oruga-backend**: ~180 MB (Python + FastAPI)
- **orion-nexus-frontend**: ~50 MB (nginx + static files)

Total: ~600 MB for all custom services (excluding FIWARE components)

---

For detailed information about each component, see:
- [README.md](../../README.md) - Overview & Quick Start
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System Architecture
- Service READMEs in each `services/*/README.md`
