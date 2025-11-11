# Sensor Configuration Update Guide

## ⚠️ Important Port Change

In the new architecture, the **Sensor Gateway has moved from Port 80 to Port 81** to allow the frontend to use Port 80.

## What Needs to Be Updated?

### IoT Sensors / Field Devices

If your sensors are configured to send data to:
```
❌ OLD: http://98.91.29.98/recibirdatos/sensor001
❌ OLD: http://98.91.29.98/recibirdatos/sensor002
```

Update them to:
```
✅ NEW: http://98.91.29.98:81/recibirdatos/sensor001
✅ NEW: http://98.91.29.98:81/recibirdatos/sensor002
```

## Port Mapping Reference

| Service | Port | URL Example |
|---------|------|-------------|
| Frontend (Web UI) | 80 | http://98.91.29.98 |
| Sensor Gateway | 81 | http://98.91.29.98:81 |
| Backend API | 8000 | http://98.91.29.98:8000 |
| ETL Service | 8080 | http://98.91.29.98:8080 |

## Update Methods

### Option 1: Update Sensor Configuration

Most IoT devices allow changing the endpoint URL. Update your sensor configuration to use port 81.

**Example for ESP8266/ESP32:**
```cpp
// Old
String serverUrl = "http://98.91.29.98/recibirdatos/sensor001";

// New
String serverUrl = "http://98.91.29.98:81/recibirdatos/sensor001";
```

**Example for Arduino:**
```cpp
// Old
const char* serverHost = "98.91.29.98";
const int serverPort = 80;

// New
const char* serverHost = "98.91.29.98";
const int serverPort = 81;  // Changed!
```

**Example for Python script:**
```python
# Old
SENSOR_GATEWAY_URL = "http://98.91.29.98/recibirdatos/sensor001"

# New
SENSOR_GATEWAY_URL = "http://98.91.29.98:81/recibirdatos/sensor001"
```

### Option 2: Use Reverse Proxy (Recommended for Production)

If you can't update sensors, use nginx as a reverse proxy to route port 80 sensor traffic to port 81.

**Create: `/etc/nginx/sites-available/sensor-proxy`**
```nginx
server {
    listen 80;
    server_name sensor.yourdomain.com;  # Or use IP
    
    # Frontend paths (serve from frontend container)
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Sensor webhook paths (route to gateway on port 81)
    location /recibirdatos/ {
        proxy_pass http://localhost:81;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/sensor-proxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Change Docker Port Mapping

If you prefer sensor gateway on port 80, modify `docker-compose.yml`:

```yaml
services:
  sensor-gateway:
    ports:
      - "80:80"    # Keep on port 80
  
  orion-nexus-frontend:
    ports:
      - "8081:80"  # Move frontend to 8081
```

**Trade-off**: Frontend will be on port 8081, which is less standard.

## Testing Updated Configuration

### Test Sensor Gateway Accessibility

**Port 81 (new):**
```powershell
# Should succeed
Invoke-RestMethod -Uri "http://98.91.29.98:81/recibirdatos/sensor001" `
  -Method Post `
  -Body '{"temperatura":{"type":"float","value":23.5},"humedad":{"type":"float","value":58.0},"token":"secreto"}' `
  -ContentType 'application/json'
```

**Port 80 (should show frontend, not gateway):**
```powershell
# Should return HTML of frontend
Invoke-WebRequest -Uri "http://98.91.29.98/"
```

### Verify Sensor Data Flow

1. Send test data from sensor
2. Check Orion: `http://98.91.29.98:1026/v2/entities`
3. Check CrateDB: `http://98.91.29.98:4200`
4. Wait for ETL (1-5 min)
5. Check processed data: `http://98.91.29.98:8080/irrigation`

## Common Issues

### Issue: Sensor Gets "Connection Refused"

**Cause**: Sensor still using port 80  
**Solution**: Update sensor config to port 81

```powershell
# Test connectivity
Test-NetConnection -ComputerName 98.91.29.98 -Port 81
```

### Issue: "404 Not Found"

**Cause**: Incorrect endpoint path  
**Solution**: Ensure path starts with `/recibirdatos/`

```
✅ Correct: http://98.91.29.98:81/recibirdatos/sensor001
❌ Wrong:   http://98.91.29.98:81/sensor001
❌ Wrong:   http://98.91.29.98:81/recibirdatos
```

### Issue: "401 Unauthorized"

**Cause**: Missing or incorrect token  
**Solution**: Ensure payload includes `"token": "secreto"`

```json
{
  "temperatura": {"type": "float", "value": 23.5},
  "humedad": {"type": "float", "value": 58.0},
  "token": "secreto"   // ← Required!
}
```

### Issue: Old Port Still Works

**Cause**: Old service still running  
**Solution**: Stop old services

```powershell
# Stop all Docker containers
docker ps -a
docker stop $(docker ps -aq)

# Restart with new compose file
docker compose up -d
```

## Rollback Plan

If you need to temporarily use port 80 for sensors:

### Quick Rollback (Temporary)

```yaml
# Edit docker-compose.yml
services:
  sensor-gateway:
    ports:
      - "80:80"        # Temporarily back to 80
  orion-nexus-frontend:
    ports:
      - "8081:80"      # Move frontend temporarily
```

```powershell
docker compose up -d
```

## Sensor Types Configuration Examples

### ESP8266/ESP32 (Arduino)

```cpp
#include <ESP8266HTTPClient.h>

const char* sensorUrl = "http://98.91.29.98:81/recibirdatos/sensor001";

void sendSensorData(float temp, float humidity) {
  HTTPClient http;
  http.begin(sensorUrl);
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"temperatura\":{\"type\":\"float\",\"value\":";
  payload += String(temp);
  payload += "},\"humedad\":{\"type\":\"float\",\"value\":";
  payload += String(humidity);
  payload += "},\"token\":\"secreto\"}";
  
  int httpCode = http.POST(payload);
  http.end();
}
```

### Raspberry Pi (Python)

```python
import requests
import json

GATEWAY_URL = "http://98.91.29.98:81/recibirdatos/sensor001"

def send_sensor_data(temperature, humidity):
    payload = {
        "temperatura": {"type": "float", "value": temperature},
        "humedad": {"type": "float", "value": humidity},
        "token": "secreto"
    }
    
    response = requests.post(
        GATEWAY_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()
```

### GPS Tracker (Any Language)

```python
import requests

GPS_URL = "http://98.91.29.98:81/recibirdatos/sensor002"

def send_location(lat, lon):
    payload = {
        "latitud": {"type": "float", "value": lat},
        "longitud": {"type": "float", "value": lon},
        "token": "secreto"
    }
    
    requests.post(GPS_URL, json=payload)
```

## Checklist

Use this checklist when updating sensors:

- [ ] Identify all sensors that need updating
- [ ] Document current sensor configurations
- [ ] Test new endpoint (port 81) manually
- [ ] Update sensor configuration (or set up proxy)
- [ ] Deploy updated configuration to sensors
- [ ] Test each sensor sends data successfully
- [ ] Verify data appears in Orion
- [ ] Verify data appears in CrateDB
- [ ] Verify ETL processes data
- [ ] Monitor for 24 hours to ensure stability
- [ ] Document any issues encountered
- [ ] Update internal documentation

## Support

If you encounter issues:

1. Test sensor gateway directly:
   ```powershell
   curl -X POST http://98.91.29.98:81/recibirdatos/sensor001 \
     -H "Content-Type: application/json" \
     -d '{"temperatura":{"type":"float","value":23},"humedad":{"type":"float","value":60},"token":"secreto"}'
   ```

2. Check sensor gateway logs:
   ```powershell
   docker compose logs sensor-gateway
   ```

3. Review [ARCHITECTURE.md](../ARCHITECTURE.md) for system overview

4. Check [TROUBLESHOOTING.md](../README.md#troubleshooting)

---

**Last Updated**: November 11, 2025  
**Change**: Sensor Gateway Port 80 → 81  
**Reason**: Frontend deployment on Port 80
