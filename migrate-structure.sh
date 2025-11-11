#!/bin/bash

# Migration Script - Reorganize Project Structure
# This script migrates the old folder structure to the new services/ hierarchy
# Run from: /path/to/Ambiente/
# IMPORTANT: This script will copy files. Review changes before deleting old folders!

echo "================================"
echo " Project Structure Migration"
echo "================================"
echo ""

rootPath="/home/ubuntu/proyecto"
cd "$rootPath" || exit 1

# Check if old folders exist
oldAgente="./agente"
oldProyectoapp="./proyectoapp"
oldOrionNexus="./orion-nexus"

if [[ ! -d "$oldAgente" && ! -d "$oldProyectoapp" && ! -d "$oldOrionNexus" ]]; then
    echo "✓ No old folders found. Migration might be already complete."
    echo "  Current structure should be in services/ folder"
    exit 0
fi

echo "Found old folder structure:"
[[ -d "$oldAgente" ]] && echo "  ✓ agente/"
[[ -d "$oldProyectoapp" ]] && echo "  ✓ proyectoapp/"
[[ -d "$oldOrionNexus" ]] && echo "  ✓ orion-nexus/"
echo ""

# Create services directory if it doesn't exist
if [[ ! -d "./services" ]]; then
    echo "Creating services/ directory..."
    mkdir -p "./services"
fi

# Migrate agente -> sensor-gateway
if [[ -d "$oldAgente" ]]; then
    echo "Migrating agente/ -> services/sensor-gateway/..."
    if [[ -d "./services/sensor-gateway" ]]; then
        echo "  ⚠ services/sensor-gateway/ already exists"
        read -rp "  Overwrite? (y/N): " response
        if [[ "$response" == "y" ]]; then
            rm -rf "./services/sensor-gateway"
        else
            echo "  Skipping sensor-gateway migration"
        fi
    fi

    if [[ ! -d "./services/sensor-gateway" ]]; then
        cp -r "$oldAgente" "./services/sensor-gateway"
        echo "  ✓ Copied to services/sensor-gateway/"
    fi
fi

# Migrate proyectoapp -> etl-service
if [[ -d "$oldProyectoapp" ]]; then
    echo "Migrating proyectoapp/ -> services/etl-service/..."
    if [[ -d "./services/etl-service" ]]; then
        echo "  ⚠ services/etl-service/ already exists"
        read -rp "  Overwrite? (y/N): " response
        if [[ "$response" == "y" ]]; then
            rm -rf "./services/etl-service"
        else
            echo "  Skipping etl-service migration"
        fi
    fi

    if [[ ! -d "./services/etl-service" ]]; then
        cp -r "$oldProyectoapp" "./services/etl-service"
        echo "  ✓ Copied to services/etl-service/"
    fi
fi

# Migrate orion-nexus -> split into frontend and backend
if [[ -d "$oldOrionNexus" ]]; then
    echo "Migrating orion-nexus/ -> services/orion-nexus-frontend/ & services/oruga-backend/..."

    # Backend
    if [[ -d "./services/oruga-backend" ]]; then
        echo "  ⚠ services/oruga-backend/ already exists"
        read -rp "  Overwrite? (y/N): " response
        if [[ "$response" == "y" ]]; then
            rm -rf "./services/oruga-backend"
        else
            echo "  Skipping oruga-backend migration"
        fi
    fi

    if [[ ! -d "./services/oruga-backend" && -d "$oldOrionNexus/backend" ]]; then
        cp -r "$oldOrionNexus/backend" "./services/oruga-backend"
        echo "  ✓ Copied backend to services/oruga-backend/"
    fi

    # Frontend
    if [[ -d "./services/orion-nexus-frontend/src" ]]; then
        echo "  ⚠ services/orion-nexus-frontend/src/ already exists"
        read -rp "  Overwrite? (y/N): " response
        if [[ "$response" == "y" ]]; then
            rm -rf "./services/orion-nexus-frontend/src"
            rm -rf "./services/orion-nexus-frontend/public"
        else
            echo "  Skipping orion-nexus-frontend source migration"
        fi
    fi

    if [[ ! -d "./services/orion-nexus-frontend/src" ]]; then
        mkdir -p "./services/orion-nexus-frontend"
        itemsToCopy=(
            "src" "public" "components.json" "package.json" "vite.config.ts"
            "tsconfig.json" "tsconfig.app.json" "tsconfig.node.json"
            "tailwind.config.ts" "postcss.config.js" "eslint.config.js"
            ".env" ".gitignore" "bun.lockb" "index.html"
        )

        for item in "${itemsToCopy[@]}"; do
            sourcePath="$oldOrionNexus/$item"
            if [[ -e "$sourcePath" ]]; then
                cp -r "$sourcePath" "./services/orion-nexus-frontend/"
            fi
        done
        echo "  ✓ Copied frontend to services/orion-nexus-frontend/"
    fi
fi

echo ""
echo "================================"
echo "Migration Summary"
echo "================================"
echo ""

# Check new structure
newSensorGateway="./services/sensor-gateway/src/main.py"
newEtlService="./services/etl-service/app.py"
newOrugaBackend="./services/oruga-backend/app/main.py"
newFrontend="./services/orion-nexus-frontend/src/App.tsx"

echo "New structure status:"
[[ -f "$newSensorGateway" ]] && echo "  ✓ services/sensor-gateway/ - OK" || echo "  ✗ services/sensor-gateway/ - Missing"
[[ -f "$newEtlService" ]] && echo "  ✓ services/etl-service/ - OK" || echo "  ✗ services/etl-service/ - Missing"
[[ -f "$newOrugaBackend" ]] && echo "  ✓ services/oruga-backend/ - OK" || echo "  ✗ services/oruga-backend/ - Missing"
[[ -f "$newFrontend" ]] && echo "  ✓ services/orion-nexus-frontend/ - OK" || echo "  ✗ services/orion-nexus-frontend/ - Missing"

echo ""
echo "================================"
echo "Next Steps"
echo "================================"
echo ""
echo "1. Verify the new structure in services/ folder"
echo "2. Test the deployment:"
echo "   docker compose up --build"
echo ""
echo "3. If everything works, delete old folders:"
echo "   rm -rf ./agente ./proyectoapp ./orion-nexus"
echo ""
echo "4. Read updated documentation:"
echo "   - README.md"
echo "   - ARCHITECTURE.md"
echo ""
echo "Migration script completed!"