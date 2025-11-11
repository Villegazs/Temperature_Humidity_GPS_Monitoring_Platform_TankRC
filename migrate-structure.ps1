# Migration Script - Reorganize Project Structure
# This script migrates the old folder structure to the new services/ hierarchy
# 
# Run from: e:\IoT\Ambiente\
# 
# IMPORTANT: This script will copy files. Review changes before deleting old folders!

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Project Structure Migration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = "e:\IoT\Ambiente"
Set-Location $rootPath

# Check if old folders exist
$oldAgente = Test-Path ".\agente"
$oldProyectoapp = Test-Path ".\proyectoapp"
$oldOrionNexus = Test-Path ".\orion-nexus"

if (-not $oldAgente -and -not $oldProyectoapp -and -not $oldOrionNexus) {
    Write-Host "✓ No old folders found. Migration might be already complete." -ForegroundColor Green
    Write-Host "  Current structure should be in services/ folder" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found old folder structure:" -ForegroundColor Yellow
if ($oldAgente) { Write-Host "  ✓ agente/" -ForegroundColor White }
if ($oldProyectoapp) { Write-Host "  ✓ proyectoapp/" -ForegroundColor White }
if ($oldOrionNexus) { Write-Host "  ✓ orion-nexus/" -ForegroundColor White }
Write-Host ""

# Create services directory if it doesn't exist
if (-not (Test-Path ".\services")) {
    Write-Host "Creating services/ directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path ".\services" -Force | Out-Null
}

# Migrate agente -> sensor-gateway
if ($oldAgente) {
    Write-Host "Migrating agente/ -> services/sensor-gateway/..." -ForegroundColor Cyan
    if (Test-Path ".\services\sensor-gateway") {
        Write-Host "  ⚠ services/sensor-gateway/ already exists" -ForegroundColor Yellow
        $response = Read-Host "  Overwrite? (y/N)"
        if ($response -eq 'y') {
            Remove-Item ".\services\sensor-gateway" -Recurse -Force
        } else {
            Write-Host "  Skipping sensor-gateway migration" -ForegroundColor Yellow
        }
    }
    
    if (-not (Test-Path ".\services\sensor-gateway")) {
        Copy-Item -Path ".\agente" -Destination ".\services\sensor-gateway" -Recurse -Force
        Write-Host "  ✓ Copied to services/sensor-gateway/" -ForegroundColor Green
    }
}

# Migrate proyectoapp -> etl-service
if ($oldProyectoapp) {
    Write-Host "Migrating proyectoapp/ -> services/etl-service/..." -ForegroundColor Cyan
    if (Test-Path ".\services\etl-service") {
        Write-Host "  ⚠ services/etl-service/ already exists" -ForegroundColor Yellow
        $response = Read-Host "  Overwrite? (y/N)"
        if ($response -eq 'y') {
            Remove-Item ".\services\etl-service" -Recurse -Force
        } else {
            Write-Host "  Skipping etl-service migration" -ForegroundColor Yellow
        }
    }
    
    if (-not (Test-Path ".\services\etl-service")) {
        Copy-Item -Path ".\proyectoapp" -Destination ".\services\etl-service" -Recurse -Force
        Write-Host "  ✓ Copied to services/etl-service/" -ForegroundColor Green
    }
}

# Migrate orion-nexus -> split into frontend and backend
if ($oldOrionNexus) {
    Write-Host "Migrating orion-nexus/ -> services/orion-nexus-frontend/ & services/oruga-backend/..." -ForegroundColor Cyan
    
    # Backend
    if (Test-Path ".\services\oruga-backend") {
        Write-Host "  ⚠ services/oruga-backend/ already exists" -ForegroundColor Yellow
        $response = Read-Host "  Overwrite? (y/N)"
        if ($response -eq 'y') {
            Remove-Item ".\services\oruga-backend" -Recurse -Force
        } else {
            Write-Host "  Skipping oruga-backend migration" -ForegroundColor Yellow
        }
    }
    
    if (-not (Test-Path ".\services\oruga-backend") -and (Test-Path ".\orion-nexus\backend")) {
        Copy-Item -Path ".\orion-nexus\backend" -Destination ".\services\oruga-backend" -Recurse -Force
        Write-Host "  ✓ Copied backend to services/oruga-backend/" -ForegroundColor Green
    }
    
    # Frontend
    if (Test-Path ".\services\orion-nexus-frontend\src") {
        Write-Host "  ⚠ services/orion-nexus-frontend/src/ already exists" -ForegroundColor Yellow
        $response = Read-Host "  Overwrite? (y/N)"
        if ($response -eq 'y') {
            # Keep dockerfile and nginx.conf, replace src
            Remove-Item ".\services\orion-nexus-frontend\src" -Recurse -Force
            Remove-Item ".\services\orion-nexus-frontend\public" -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "  Skipping orion-nexus-frontend source migration" -ForegroundColor Yellow
        }
    }
    
    if (-not (Test-Path ".\services\orion-nexus-frontend\src")) {
        # Copy frontend files (excluding backend folder)
        $itemsToCopy = @(
            "src", "public", "components.json", "package.json", "vite.config.ts",
            "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json",
            "tailwind.config.ts", "postcss.config.js", "eslint.config.js",
            ".env", ".gitignore", "bun.lockb", "index.html"
        )
        
        foreach ($item in $itemsToCopy) {
            $sourcePath = ".\orion-nexus\$item"
            if (Test-Path $sourcePath) {
                Copy-Item -Path $sourcePath -Destination ".\services\orion-nexus-frontend\" -Recurse -Force
            }
        }
        Write-Host "  ✓ Copied frontend to services/orion-nexus-frontend/" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Migration Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check new structure
$newSensorGateway = Test-Path ".\services\sensor-gateway\src\main.py"
$newEtlService = Test-Path ".\services\etl-service\app.py"
$newOrugaBackend = Test-Path ".\services\oruga-backend\app\main.py"
$newFrontend = Test-Path ".\services\orion-nexus-frontend\src\App.tsx"

Write-Host "New structure status:" -ForegroundColor Yellow
if ($newSensorGateway) {
    Write-Host "  ✓ services/sensor-gateway/ - OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ services/sensor-gateway/ - Missing" -ForegroundColor Red
}

if ($newEtlService) {
    Write-Host "  ✓ services/etl-service/ - OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ services/etl-service/ - Missing" -ForegroundColor Red
}

if ($newOrugaBackend) {
    Write-Host "  ✓ services/oruga-backend/ - OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ services/oruga-backend/ - Missing" -ForegroundColor Red
}

if ($newFrontend) {
    Write-Host "  ✓ services/orion-nexus-frontend/ - OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ services/orion-nexus-frontend/ - Missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Verify the new structure in services/ folder" -ForegroundColor White
Write-Host "2. Test the deployment:" -ForegroundColor White
Write-Host "   docker compose up --build" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. If everything works, delete old folders:" -ForegroundColor White
Write-Host "   Remove-Item -Recurse .\agente, .\proyectoapp, .\orion-nexus" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Read updated documentation:" -ForegroundColor White
Write-Host "   - README.md" -ForegroundColor Cyan
Write-Host "   - ARCHITECTURE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Migration script completed!" -ForegroundColor Green
