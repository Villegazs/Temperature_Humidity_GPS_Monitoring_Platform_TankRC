# ETL Service - Orion Context Broker Integration

Este servicio maneja la integración completa con Orion Context Broker, incluyendo:

- 🔄 **ETL Processing**: Procesamiento de datos de irrigación y GPS
- 📡 **Automatic Subscriptions**: Suscripciones automáticas para sensores
- 🏗️ **Entity Management**: Creación y gestión de entidades de sensores
- 🔍 **Monitoring**: Endpoints para monitoreo y health checks

## Características Principales

### 1. Suscripciones Automáticas

El servicio crea automáticamente suscripciones para:

- **Sensores de Temperatura/Humedad** (`sensorTempHum`)
  - Atributos: `temperatura`, `humedad`
  - Notificaciones enviadas a QuantumLeap

- **Sensores GPS** (`sensorGPS`)
  - Atributos: `latitud`, `longitud`
  - Notificaciones enviadas a QuantumLeap

### 2. Entidades de Sensores Iniciales

Crea automáticamente las siguientes entidades:

#### Sensor de Temperatura/Humedad
```json
{
  "id": "sensor001",
  "type": "sensorTempHum",
  "temperatura": {
    "value": 25.1,
    "type": "float"
  },
  "humedad": {
    "value": 58.5,
    "type": "float"
  }
}
```

#### Sensor GPS
```json
{
  "id": "sensor002",
  "type": "sensorGPS",
  "latitud": {
    "value": 6.26195,
    "type": "float"
  },
  "longitud": {
    "value": -75.59046,
    "type": "float"
  }
}
```

## API Endpoints

### Endpoints Principales

- `GET /etl` - Información del servicio y endpoints disponibles
- `GET /irrigation` - Datos de irrigación más recientes
- `GET /gps` - Datos de GPS más recientes

### Endpoints de Suscripciones

- `GET /subscriptions` - Lista todas las suscripciones activas
- `GET /subscriptions/health` - Health check del sistema
- `POST /subscriptions/recreate` - Recrea las suscripciones automáticas

### Endpoints de Entidades

- `GET /subscriptions/entities` - Lista todas las entidades
- `POST /subscriptions/entities/setup` - Configura entidades iniciales
- `GET /subscriptions/entities/{entity_id}` - Obtiene entidad específica

## Configuración

### Variables de Entorno

```bash
ORION_URL=http://orion:1026          # URL de Orion Context Broker
PYTHONPATH=/app                      # Path de Python
```

### Archivos de Configuración

- `configuration.py` - Configuración principal del servicio
- `subscriptions.py` - Gestión de suscripciones automáticas
- `entities.py` - Gestión de entidades de sensores

## Uso

### 1. Inicio Automático

El servicio se inicia automáticamente con:
1. ✅ Conexión a bases de datos (CrateDB, MongoDB)
2. ✅ Configuración de suscripciones automáticas
3. ✅ Creación de entidades iniciales
4. ✅ Inicio de schedulers en background
5. ✅ Ejecución de ETLs iniciales

### 2. Verificación del Estado

```bash
# Health check general
curl http://localhost:8080/subscriptions/health

# Listar entidades
curl http://localhost:8080/subscriptions/entities

# Verificar entidad específica
curl http://localhost:8080/subscriptions/entities/sensor001
```

### 3. Recreación Manual

Si necesitas recrear las suscripciones o entidades:

```bash
# Recrear suscripciones
curl -X POST http://localhost:8080/subscriptions/recreate

# Recrear entidades
curl -X POST http://localhost:8080/subscriptions/entities/setup
```

## Testing

Ejecuta el script de pruebas integradas:

```bash
python test_integration.py
```

Este script verifica:
- ✅ Conectividad del servicio ETL
- ✅ Estado del sistema de suscripciones
- ✅ Acceso directo a Orion Context Broker
- ✅ Listado y acceso a entidades
- ✅ Configuración automática si es necesaria

## Troubleshooting

### Problemas Comunes

1. **ModuleNotFoundError: No module named 'config'**
   - ✅ **Solucionado**: Ahora usa `import configuration as config`

2. **Suscripciones no se crean**
   - Verifica que Orion Context Broker esté accesible
   - Revisa los logs del contenedor
   - Usa `POST /subscriptions/recreate`

3. **Entidades no aparecen**
   - Usa `POST /subscriptions/entities/setup`
   - Verifica headers FIWARE (Service: smart, ServicePath: /)

### Logs y Debugging

```bash
# Ver logs del contenedor
docker logs etl-service

# Verificar conectividad a Orion
docker exec -it etl-service curl http://orion:1026/version

# Verificar entidades directamente en Orion
curl -H "Fiware-Service: smart" -H "Fiware-ServicePath: /" \
     http://localhost:1026/v2/entities
```

## Estructura de Archivos

```
etl-service/
├── app.py                      # Aplicación principal
├── configuration.py            # Configuración del servicio
├── subscriptions.py           # Gestión de suscripciones
├── entities.py                # Gestión de entidades
├── utils.py                   # Utilidades compartidas
├── scheduler.py               # Schedulers en background
├── test_integration.py        # Script de pruebas
├── requirements.txt           # Dependencias Python
├── dockerfile                 # Configuración Docker
├── routes/
│   ├── irrigation_routes.py   # Rutas de irrigación
│   ├── gps_routes.py         # Rutas de GPS
│   └── subscriptions_routes.py # Rutas de suscripciones
└── services/
    ├── irrigation_service.py  # Servicio de irrigación
    └── gps_service.py        # Servicio de GPS
```

## Próximos Pasos

1. **Implementar autenticación** para endpoints sensibles
2. **Agregar más tipos de sensores** según necesidades
3. **Implementar métricas** y alertas avanzadas
4. **Crear dashboard** para monitoreo en tiempo real