# Quick Start Guide

## Prerequisites Check

Before starting, verify you have:

```powershell
# Docker
docker --version
# Should show: Docker version 20.10+

# Docker Compose
docker compose version
# Should show: Docker Compose version v2+

# Check available RAM (should be 8GB+)
Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum | Select-Object @{N="Total RAM (GB)"; E={[math]::round($_.sum / 1GB, 2)}}
```

## 🚀 5-Minute Setup

### 1. Clone & Navigate
```powershell
cd e:\IoT\Ambiente
```

### 2. Start Services
```powershell
# Build and start all services in background
docker compose up -d --build

# This will take 3-5 minutes on first run
```

### 3. Monitor Startup
```powershell
# Watch logs to see when services are ready
docker compose logs -f

# Press Ctrl+C to stop watching (services keep running)
```

### 4. Check Status
```powershell
# All services should show "Up" and "healthy"
docker compose ps
```

### 5. Access Services

Open in your browser:
- **Web UI**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **CrateDB**: http://localhost:4200

## 🧪 Test the System

### Test 1: Send Temperature Data
```powershell
Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor001" `
  -Method Post `
  -Body '{"temperatura":{"type":"float","value":25.5},"humedad":{"type":"float","value":60.0},"token":"secreto"}' `
  -ContentType 'application/json'
```

**Expected**: `{"mensaje":"Datos recibidos y procesados correctamente."}`

### Test 2: Send GPS Data
```powershell
Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor002" `
  -Method Post `
  -Body '{"latitud":{"type":"float","value":6.26195},"longitud":{"type":"float","value":-75.59046},"token":"secreto"}' `
  -ContentType 'application/json'
```

**Expected**: `{"mensaje":"Datos recibidos y procesados correctamente."}`

### Test 3: Check Orion Entities
```powershell
# Should show sensor001 and sensor002
Invoke-RestMethod -Uri "http://localhost:1026/v2/entities"
```

### Test 4: Wait for ETL Processing
```powershell
# Wait 1-5 minutes for ETL to run
# Check irrigation KPI
Invoke-RestMethod -Uri "http://localhost:8080/irrigation"

# Check GPS location
Invoke-RestMethod -Uri "http://localhost:8080/gps"
```

## 📊 Verify Data Flow

### 1. Check CrateDB (Raw Data)
Visit: http://localhost:4200

Run query:
```sql
SELECT * FROM etsensortemphum ORDER BY time_index DESC LIMIT 5;
SELECT * FROM etsensorgps ORDER BY time_index DESC LIMIT 5;
```

### 2. Check MongoDB (Processed Data)
```powershell
# Connect to MongoDB
docker exec -it db-mongo mongo

# In mongo shell:
use sprinkler_db
db.riego_kpi.find().sort({timestamp: -1}).limit(1).pretty()

use gps_db
db.location_history.find().sort({timestamp: -1}).limit(1).pretty()

# Type 'exit' to leave mongo shell
```

### 3. View in Grafana
1. Open http://localhost:3000
2. Login: admin/admin
3. Add CrateDB data source
4. Create dashboard with sensor data

## 🎯 Common Tasks

### View Service Logs
```powershell
# All services
docker compose logs -f

# Specific service
docker compose logs -f etl-service
```

### Restart a Service
```powershell
docker compose restart orion-nexus-frontend
```

### Stop Everything
```powershell
docker compose down
```

### Stop and Clean Volumes
```powershell
# WARNING: This deletes all data!
docker compose down -v
```

### Rebuild After Code Changes
```powershell
docker compose up -d --build <service-name>

# Example:
docker compose up -d --build orion-nexus-frontend
```

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find what's using port 80
Get-NetTCPConnection -LocalPort 80 | Select-Object OwningProcess

# Stop the process
Stop-Process -Id <process_id>
```

### Service Not Starting
```powershell
# Check logs for errors
docker compose logs <service-name>

# Restart the service
docker compose restart <service-name>
```

### Can't Connect to Database
```powershell
# Check if databases are healthy
docker compose ps

# Restart database
docker compose restart mongo-db
docker compose restart crate-db
```

### Frontend Shows Blank Page
```powershell
# Check build logs
docker compose logs orion-nexus-frontend

# Rebuild
docker compose up -d --build orion-nexus-frontend
```

## 🔧 Development Mode

### Work on Frontend
```bash
cd services/orion-nexus-frontend
npm install
npm run dev
# Access at http://localhost:5173
```

### Work on Backend
```bash
cd services/oruga-backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Access at http://localhost:8000
```

### Work on ETL Service
```bash
cd services/etl-service
pip install -r requirements.txt
python app.py
# Access at http://localhost:8080
```

## 📱 Send Test Data Continuously

Create a test script:

```powershell
# test-sensors.ps1
while ($true) {
    $temp = Get-Random -Minimum 15 -Maximum 35
    $humidity = Get-Random -Minimum 40 -Maximum 80
    
    Write-Host "Sending temp: $temp, humidity: $humidity"
    
    Invoke-RestMethod -Uri "http://localhost:81/recibirdatos/sensor001" `
      -Method Post `
      -Body "{`"temperatura`":{`"type`":`"float`",`"value`":$temp},`"humedad`":{`"type`":`"float`",`"value`":$humidity},`"token`":`"secreto`"}" `
      -ContentType 'application/json'
    
    Start-Sleep -Seconds 10
}
```

Run it:
```powershell
.\test-sensors.ps1
```

## 🎓 Next Steps

1. **Explore the Web UI**: http://localhost
2. **Read the docs**: Open `ARCHITECTURE.md`
3. **Customize**: Edit service configurations
4. **Add sensors**: Follow sensor integration guide in README.md
5. **Create dashboards**: Use Grafana to visualize data
6. **Deploy**: Review deployment guide for production

## 📚 Documentation Quick Links

- [README.md](./README.md) - Main documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md) - Directory guide
- [MIGRATION_GUIDE.md](./docs/deployment/MIGRATION_GUIDE.md) - Upgrade instructions

## 🆘 Getting Help

If something doesn't work:

1. Check service status: `docker compose ps`
2. View logs: `docker compose logs -f`
3. Review [ARCHITECTURE.md](./ARCHITECTURE.md)
4. Check individual service READMEs
5. Open an issue in the repository

## ✅ Success Checklist

You're all set when:

- [ ] All services show "Up (healthy)" in `docker compose ps`
- [ ] Frontend loads at http://localhost
- [ ] Backend API docs load at http://localhost:8000/docs
- [ ] Test sensor data returns success
- [ ] Data appears in CrateDB
- [ ] ETL processes data into MongoDB
- [ ] Irrigation KPI is calculated
- [ ] GPS location is tracked

## 🎉 You're Ready!

Your FIWARE IoT platform is now running. Start sending real sensor data or explore the web interface!

---

**Time to complete**: 5-10 minutes  
**Last updated**: November 11, 2025  
**Version**: 2.0
