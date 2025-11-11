# Documentation Index

Welcome to the Temperature, Humidity & GPS Monitoring Platform documentation.

## 📚 Documentation Structure

```
docs/
├── README.md (this file)          # Documentation index
├── PROJECT_STRUCTURE.md           # Visual directory structure
├── REORGANIZATION_SUMMARY.md      # What changed in v2.0
├── api/                           # API specifications
├── deployment/
│   └── MIGRATION_GUIDE.md        # How to migrate from v1.0
└── sensors/
    └── SENSOR_CONFIGURATION_UPDATE.md  # Update sensor endpoints
```

## 🚀 Getting Started

Choose your path:

### I'm New Here
1. Start with [QUICKSTART.md](../QUICKSTART.md) - 5 minutes
2. Read [README.md](../README.md) - Overview & basics
3. Explore [ARCHITECTURE.md](../ARCHITECTURE.md) - How it all works

### I Want to Migrate from v1.0
1. Read [MIGRATION_GUIDE.md](./deployment/MIGRATION_GUIDE.md)
2. Run the migration script
3. Update sensor configurations (see below)

### I Want to Develop
1. Read [ARCHITECTURE.md](../ARCHITECTURE.md)
2. Review [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
3. Check service-specific READMEs in `../services/*/README.md`

### I Need to Deploy Sensors
1. Read [Sensor Integration](../README.md#sensor-integration) in main README
2. Update configurations: [SENSOR_CONFIGURATION_UPDATE.md](./sensors/SENSOR_CONFIGURATION_UPDATE.md)

## 📖 Main Documentation

### [README.md](../README.md) - Main Documentation
**Read this first** for a complete overview of the project.

**Contents:**
- System overview and components
- Quick start guide
- Service descriptions
- Sensor integration
- REST API endpoints
- Operations and monitoring
- Troubleshooting

**When to read:** Always start here

---

### [QUICKSTART.md](../QUICKSTART.md) - 5-Minute Setup
**Fast track** to getting the system running.

**Contents:**
- Prerequisites check
- Build and start commands
- Test procedures
- Common tasks
- Development mode

**When to read:** When you want to deploy quickly

---

### [ARCHITECTURE.md](../ARCHITECTURE.md) - System Architecture
**Deep dive** into how everything works together.

**Contents:**
- Complete architecture diagrams
- Service dependency graph
- Data flow explanations
- Port mapping
- Configuration details
- Deployment strategies
- Scalability considerations

**When to read:** Understanding system design, planning changes

---

### [CHANGELOG.md](../CHANGELOG.md) - Version History
**What changed** between versions.

**Contents:**
- Version 2.0 changes
- Breaking changes
- New features
- Migration requirements

**When to read:** Before upgrading, understanding changes

---

## 📂 Detailed Documentation

### [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
**Visual guide** to the directory structure.

**Contents:**
- Complete directory tree with descriptions
- File purpose guide
- Service dependency graphs
- Quick navigation commands

**When to read:** Finding files, understanding organization

---

### [REORGANIZATION_SUMMARY.md](./REORGANIZATION_SUMMARY.md)
**Before/after comparison** of the project structure.

**Contents:**
- What was done
- Architecture comparison
- New files created
- Data flow examples
- Impact summary

**When to read:** Understanding v2.0 changes

---

## 🚀 Deployment Documentation

### [MIGRATION_GUIDE.md](./deployment/MIGRATION_GUIDE.md)
**Step-by-step guide** to migrate from v1.0 to v2.0.

**Contents:**
- What changed
- Migration methods (automatic & manual)
- Verification steps
- Configuration changes
- Port changes
- Common issues
- Rollback procedures

**When to read:** Upgrading from old structure

---

## 📡 Sensor Documentation

### [SENSOR_CONFIGURATION_UPDATE.md](./sensors/SENSOR_CONFIGURATION_UPDATE.md)
**Update guide** for sensor endpoints after port change.

**Contents:**
- Port change explanation (80 → 81)
- Update methods
- Configuration examples for different sensor types
- Testing procedures
- Troubleshooting

**When to read:** After migration, updating sensors

---

## 🛠️ Service Documentation

Each service has its own README:

### [sensor-gateway/README.md](../services/sensor-gateway/README.md)
- Purpose and features
- API endpoints
- Security (token validation)
- Supported sensors

### [etl-service/README.md](../services/etl-service/README.md)
- ETL processes (Irrigation & GPS)
- REST API endpoints
- Scheduling details
- Architecture

### [oruga-backend/README.md](../services/oruga-backend/README.md)
- FastAPI endpoints
- Health checks
- Configuration
- Development setup

### [orion-nexus-frontend/README.md](../services/orion-nexus-frontend/README.md)
- React application
- Build process
- Environment variables
- Development workflow

---

## 📋 Documentation by Task

### Deployment & Operations

| Task | Document |
|------|----------|
| First-time setup | [QUICKSTART.md](../QUICKSTART.md) |
| Migrate from v1.0 | [MIGRATION_GUIDE.md](./deployment/MIGRATION_GUIDE.md) |
| Update sensors | [SENSOR_CONFIGURATION_UPDATE.md](./sensors/SENSOR_CONFIGURATION_UPDATE.md) |
| Monitor services | [README.md - Operations](../README.md#operations) |
| Troubleshooting | [README.md - Troubleshooting](../README.md#troubleshooting) |

### Development

| Task | Document |
|------|----------|
| Understand system | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Find files | [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) |
| Develop frontend | [orion-nexus-frontend/README.md](../services/orion-nexus-frontend/README.md) |
| Develop backend | [oruga-backend/README.md](../services/oruga-backend/README.md) |
| Develop ETL | [etl-service/README.md](../services/etl-service/README.md) |
| Add sensors | [sensor-gateway/README.md](../services/sensor-gateway/README.md) |

### Integration

| Task | Document |
|------|----------|
| Integrate sensors | [README.md - Sensor Integration](../README.md#sensor-integration) |
| Use REST APIs | [README.md - REST API Endpoints](../README.md#rest-api-endpoints) |
| Backend API | [oruga-backend/README.md](../services/oruga-backend/README.md) |
| ETL API | [etl-service/README.md](../services/etl-service/README.md) |

---

## 🔍 Quick Reference

### Port Map
| Service | Port | URL |
|---------|------|-----|
| Frontend | 80 | http://localhost |
| Sensor Gateway | 81 | http://localhost:81 |
| Backend API | 8000 | http://localhost:8000 |
| ETL Service | 8080 | http://localhost:8080 |
| Orion | 1026 | http://localhost:1026 |
| Grafana | 3000 | http://localhost:3000 |
| CrateDB | 4200 | http://localhost:4200 |
| MongoDB | 27017 | mongodb://localhost:27017 |

### Key Commands
```powershell
# Start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and clean data
docker compose down -v
```

### Sensor Endpoints
```
# Temperature & Humidity
POST http://localhost:81/recibirdatos/sensor001

# GPS Location
POST http://localhost:81/recibirdatos/sensor002
```

---

## 🎓 Learning Path

### For New Users (30 minutes)
1. [QUICKSTART.md](../QUICKSTART.md) - 5 min
2. [README.md](../README.md) - 15 min
3. [ARCHITECTURE.md](../ARCHITECTURE.md) - 10 min
4. Explore web UI - hands-on

### For Developers (1 hour)
1. [README.md](../README.md) - 15 min
2. [ARCHITECTURE.md](../ARCHITECTURE.md) - 20 min
3. [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 10 min
4. Service READMEs - 15 min
5. Code exploration - hands-on

### For Operators (45 minutes)
1. [QUICKSTART.md](../QUICKSTART.md) - 5 min
2. [README.md - Operations](../README.md#operations) - 15 min
3. [SENSOR_CONFIGURATION_UPDATE.md](./sensors/SENSOR_CONFIGURATION_UPDATE.md) - 10 min
4. [README.md - Troubleshooting](../README.md#troubleshooting) - 15 min

### For Migration (20 minutes)
1. [MIGRATION_GUIDE.md](./deployment/MIGRATION_GUIDE.md) - 10 min
2. [REORGANIZATION_SUMMARY.md](./REORGANIZATION_SUMMARY.md) - 5 min
3. [SENSOR_CONFIGURATION_UPDATE.md](./sensors/SENSOR_CONFIGURATION_UPDATE.md) - 5 min

---

## 🆘 Getting Help

1. **Check documentation** above for your specific task
2. **Search** using Ctrl+F in documentation files
3. **Review logs** with `docker compose logs -f`
4. **Check** the [Troubleshooting](../README.md#troubleshooting) section
5. **Open an issue** in the repository

---

## 📝 Documentation Standards

All documentation follows these principles:

- **Clear structure** with table of contents
- **Code examples** for all commands
- **Visual diagrams** where helpful
- **Step-by-step** instructions
- **Troubleshooting** sections
- **Cross-references** between docs

---

## 🤝 Contributing to Documentation

To improve documentation:

1. Identify what's unclear or missing
2. Create/update markdown files
3. Follow existing structure and style
4. Add to this index if creating new docs
5. Submit pull request

---

**Last Updated**: November 11, 2025  
**Version**: 2.0  
**Total Documentation**: 2,000+ lines across 12 files
