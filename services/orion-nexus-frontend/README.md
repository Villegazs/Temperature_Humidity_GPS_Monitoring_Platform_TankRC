# Orion Nexus Frontend

React + TypeScript + Vite frontend for managing FIWARE Orion Context Broker entities.

## Features
- Entity management interface
- Real-time data visualization
- Controller dashboard for IoT devices
- Built with shadcn/ui components

## Development
```bash
npm install
npm run dev
```

## Production Build
```bash
npm run build
```

## Environment Variables
Copy `.env.example` to `.env` and configure:
- `VITE_API_URL` - Backend API endpoint
- `VITE_ORION_URL` - Orion Context Broker URL

## Docker Deployment
Built automatically as part of docker-compose stack on port 80.
