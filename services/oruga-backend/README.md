# Oruga Backend

FastAPI backend service for managing FIWARE Orion Context Broker entities and commands.

## Purpose
Provides a modern REST API layer on top of Orion Context Broker with additional business logic and command handling capabilities.

## Features
- FastAPI with automatic OpenAPI documentation
- CORS enabled for frontend integration
- Health check endpoint with Orion connectivity status
- Command routing for IoT device management

## API Endpoints

### Health Check
```
GET /health
```
Returns service status and Orion connectivity.

### Orion Commands
```
Prefix: /api/v1
```
See `/docs` for full API documentation when running.

## Environment
- Port: 8000
- Dependencies: FastAPI, Uvicorn, Requests, Pydantic
- Orion connection: `http://orion:1026`

## Configuration
Environment variables (`.env`):
- `APP_NAME` - Application name
- `API_PREFIX` - API route prefix (default: `/api/v1`)
- `ORION_HOST` - Orion Context Broker URL

## Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentation
Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
