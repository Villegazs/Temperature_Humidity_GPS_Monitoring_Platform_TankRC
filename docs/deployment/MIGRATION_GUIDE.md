# Migration Guide

## Overview
This guide helps you migrate from the old folder structure to the new modular services architecture.

## What Changed?

### Old Structure ❌
```
e:/IoT/Ambiente/
├── agente/                    # Sensor gateway
├── proyectoapp/              # ETL service
├── orion-nexus/              # Combined frontend + backend
│   ├── backend/
│   └── src/
└── docker-compose.yml
```

### New Structure ✅
```
e:/IoT/Ambiente/
├── services/                  # All custom services
│   ├── sensor-gateway/       # Formerly: agente/
│   ├── etl-service/          # Formerly: proyectoapp/
│   ├── oruga-backend/        # Formerly: orion-nexus/backend/
│   └── orion-nexus-frontend/ # Formerly: orion-nexus/ (root files)
├── docs/                      # Documentation
├── docker-compose.yml         # Updated paths
└── ARCHITECTURE.md           # New architecture guide
```

## Migration Methods

### Method 1: Automatic Migration (Recommended)

Run the PowerShell migration script:

```powershell
cd e:\IoT\Ambiente
.\migrate-structure.ps1
```

This script will:
1. Create `services/` directory
2. Copy files to new locations
3. Verify the migration
4. Show next steps

**Important:** The script copies files (doesn't move them) so you can verify before deleting old folders.

### Method 2: Manual Migration

If you prefer manual control:

#### Step 1: Create New Structure
```powershell
cd e:\IoT\Ambiente
New-Item -ItemType Directory -Path "services" -Force
```

#### Step 2: Copy Sensor Gateway
```powershell
Copy-Item -Recurse .\agente .\services\sensor-gateway
```

#### Step 3: Copy ETL Service
```powershell
Copy-Item -Recurse .\proyectoapp .\services\etl-service
```

#### Step 4: Copy Backend
```powershell
Copy-Item -Recurse .\orion-nexus\backend .\services\oruga-backend
```

#### Step 5: Copy Frontend
```powershell
# Copy all frontend files except backend folder
$items = @("src", "public", "package.json", "vite.config.ts", "tsconfig.json", 
           "tailwind.config.ts", "index.html", ".env", "components.json")
           
foreach ($item in $items) {
    if (Test-Path ".\orion-nexus\$item") {
        Copy-Item -Recurse ".\orion-nexus\$item" ".\services\orion-nexus-frontend\"
    }
}

# Copy the new dockerfile and nginx.conf (already created)
# These files are already in services/orion-nexus-frontend/ from the setup
```

## Verification

### 1. Check File Structure
```powershell
# Should show all service folders
Get-ChildItem .\services\

# Verify key files exist
Test-Path .\services\sensor-gateway\src\main.py
Test-Path .\services\etl-service\app.py
Test-Path .\services\oruga-backend\app\main.py
Test-Path .\services\orion-nexus-frontend\src\App.tsx
```

### 2. Test the New Structure
```powershell
# Build and run with new docker-compose.yml
docker compose up --build

# Check all services are running
docker compose ps

# Check logs for any errors
docker compose logs
```

### 3. Verify Services

**Test Frontend (Port 80):**
```powershell
# Should show the web interface
Start-Process "http://localhost"
```

**Test Backend API (Port 8000):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
# Should return: {"status":"ok","orion":"reachable","app":"Oruga Backend"}
```

**Test ETL Service (Port 8080):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/"
# Should return service info
```

**Test Sensor Gateway (Port 81):**
```powershell
Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor001" `
  -Method Post `
  -Body '{"temperatura":{"type":"float","value":23.5},"humedad":{"type":"float","value":58.0},"token":"secreto"}' `
  -ContentType 'application/json'
# Should return: {"mensaje":"Datos recibidos y procesados correctamente."}
```

## Cleanup

### After Successful Migration

Once you've verified everything works:

```powershell
# Stop services
docker compose down

# Remove old folders
Remove-Item -Recurse -Force .\agente
Remove-Item -Recurse -Force .\proyectoapp
Remove-Item -Recurse -Force .\orion-nexus

# Restart with clean slate
docker compose up --build
```

### If Something Went Wrong

Rollback by:
1. Stop containers: `docker compose down`
2. Delete `services/` folder
3. Use old docker-compose.yml (if you backed it up)
4. Report the issue

## Configuration Changes

### Environment Variables

**Oruga Backend** needs `.env` file:
```powershell
# Create .env in oruga-backend
Copy-Item .\services\oruga-backend\.env.example .\services\oruga-backend\.env

# Edit with your settings
notepad .\services\oruga-backend\.env
```

**Frontend** may need environment variables:
```powershell
# Copy example
Copy-Item .\services\orion-nexus-frontend\.env.example .\services\orion-nexus-frontend\.env

# Edit if needed
notepad .\services\orion-nexus-frontend\.env
```

### Docker Compose

The new `docker-compose.yml` has updated:
- Service names (more descriptive)
- Build paths (pointing to `services/`)
- Port mappings (frontend on 80, gateway on 81)
- Health checks (improved monitoring)
- Dependencies (explicit wait conditions)

**No action needed** - the file is already updated.

## Port Changes

| Service | Old Port | New Port | Notes |
|---------|----------|----------|-------|
| Frontend | - | 80 | New service |
| Backend | 8000 | 8000 | Unchanged |
| ETL | 8080 | 8080 | Unchanged |
| Sensor Gateway | 80 | 81 | **Changed to avoid conflict** |
| Orion | 1026 | 1026 | Unchanged |
| Grafana | 3000 | 3000 | Unchanged |
| CrateDB | 4200 | 4200 | Unchanged |
| MongoDB | 27017 | 27017 | Unchanged |

### Update Sensor Configurations

If your sensors are configured to send to `http://server:80/recibirdatos/sensor001`:

**Update to:** `http://server:81/recibirdatos/sensor001`

Or update docker-compose.yml to map sensor-gateway to port 80 if needed.

## Common Issues

### Issue: "Port 80 is already in use"

**Solution 1:** Stop conflicting service
```powershell
# Find what's using port 80
Get-NetTCPConnection -LocalPort 80 | Select-Object OwningProcess
Stop-Process -Id <process_id>
```

**Solution 2:** Change frontend port in docker-compose.yml
```yaml
orion-nexus-frontend:
  ports:
    - "8081:80"  # Access at http://localhost:8081
```

### Issue: "Cannot connect to Orion"

Check Orion is running:
```powershell
docker compose logs orion
curl http://localhost:1026/version
```

### Issue: "ETL service can't find config.py"

The import might be wrong. In `etl-service`:
```python
# Change from:
from proyectoapp.services.irrigation_service import etl_process_irrigation

# To:
from services.irrigation_service import etl_process_irrigation
```

### Issue: "Frontend shows 404"

1. Check nginx is serving files:
   ```powershell
   docker compose exec orion-nexus-frontend ls /usr/share/nginx/html
   ```
2. Check build succeeded:
   ```powershell
   docker compose logs orion-nexus-frontend
   ```
3. Rebuild:
   ```powershell
   docker compose up --build orion-nexus-frontend
   ```

## Benefits of New Structure

### ✅ Modularity
Each service is self-contained with its own:
- Dockerfile
- Dependencies (requirements.txt / package.json)
- README documentation
- Configuration

### ✅ Scalability
Services can be scaled independently:
```powershell
docker compose up -d --scale sensor-gateway=3
```

### ✅ Development
Easier to work on individual services:
```bash
cd services/oruga-backend
# Only this service's dependencies
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### ✅ Documentation
Clear separation with service-specific READMEs and centralized ARCHITECTURE.md

### ✅ Frontend Separation
React app now served by nginx (production-ready) instead of Vite dev server

## Need Help?

1. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system overview
2. Review service-specific READMEs in `services/*/README.md`
3. Check Docker logs: `docker compose logs <service-name>`
4. Open an issue in the repository

## Migration Checklist

- [ ] Backup current working directory
- [ ] Run migration script or manual steps
- [ ] Verify new folder structure exists
- [ ] Update .env files if needed
- [ ] Build containers: `docker compose up --build`
- [ ] Test all services (frontend, backend, ETL, sensors)
- [ ] Verify data flows (send test sensor data)
- [ ] Check Grafana dashboards
- [ ] Update sensor configurations (if port changed)
- [ ] Update documentation/deployment scripts with new paths
- [ ] Delete old folders (after verification)
- [ ] Commit changes to version control

---

**Migration Date:** November 11, 2025  
**Version:** 2.0 (Modular Services Architecture)
