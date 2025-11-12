#!/bin/bash

# Script para diagnosticar problemas con suscripciones de Orion Context Broker
# Ejecutar desde la terminal para troubleshooting

echo "=========================================="
echo "🔧 Diagnóstico de Suscripciones Orion"
echo "=========================================="

# Variables - Reemplaza PUBLIC_IP_HERE con la IP pública real de tu instancia AWS
PUBLIC_IP="PUBLIC_IP_HERE"  # ⚠️ CAMBIAR POR LA IP PÚBLICA REAL
ETL_SERVICE="http://${PUBLIC_IP}:8080"
ORION_URL="http://${PUBLIC_IP}:1026"

echo ""
echo "1. 🔍 Verificando conectividad de servicios..."

# Verificar ETL Service
echo "   • ETL Service:"
if curl -s "$ETL_SERVICE/etl" >/dev/null; then
    echo "     ✓ ETL Service accesible en $ETL_SERVICE"
else
    echo "     ✗ ETL Service NO accesible en $ETL_SERVICE"
fi

# Verificar Orion Context Broker
echo "   • Orion Context Broker:"
if curl -s "$ORION_URL/version" >/dev/null; then
    echo "     ✓ Orion Context Broker accesible en $ORION_URL"
    ORION_VERSION=$(curl -s "$ORION_URL/version" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "     ℹ Versión: $ORION_VERSION"
else
    echo "     ✗ Orion Context Broker NO accesible en $ORION_URL"
fi

echo ""
echo "2. 📊 Health check del sistema de suscripciones..."
curl -s "$ETL_SERVICE/subscriptions/health" | jq '.'

echo ""
echo "3. 📋 Listando suscripciones (con comparación de headers)..."
curl -s "$ETL_SERVICE/subscriptions" | jq '.'

echo ""
echo "4. 🏗️ Listando entidades..."
curl -s "$ETL_SERVICE/subscriptions/entities" | jq '.'

echo ""
echo "5. 🔍 Consulta directa a Orion (sin headers FIWARE)..."
echo "   URL: $ORION_URL/v2/subscriptions"
curl -s -H "Accept: application/json" "$ORION_URL/v2/subscriptions" | jq '.'

echo ""
echo "6. 🔍 Consulta directa a Orion (con headers FIWARE)..."
echo "   URL: $ORION_URL/v2/subscriptions"
echo "   Headers: Fiware-Service: smart, Fiware-ServicePath: /"
curl -s -H "Accept: application/json" \
     -H "Fiware-Service: smart" \
     -H "Fiware-ServicePath: /" \
     "$ORION_URL/v2/subscriptions" | jq '.'

echo ""
echo "7. 🏗️ Consulta directa de entidades en Orion..."
curl -s -H "Accept: application/json" \
     -H "Fiware-Service: smart" \
     -H "Fiware-ServicePath: /" \
     "$ORION_URL/v2/entities" | jq '.'

echo ""
echo "8. 🛠️ Debug completo via ETL Service..."
curl -s "$ETL_SERVICE/subscriptions/debug" | jq '.'

echo ""
echo "=========================================="
echo "📝 Recomendaciones:"
echo "=========================================="
echo "• Si las suscripciones aparecen con headers FIWARE pero no sin ellos,"
echo "  es normal - las suscripciones están en el tenant 'smart'"
echo ""
echo "• Si NO aparecen suscripciones con headers FIWARE, ejecuta:"
echo "  curl -X POST $ETL_SERVICE/subscriptions/recreate"
echo ""
echo "• Si las entidades NO aparecen, ejecuta:"
echo "  curl -X POST $ETL_SERVICE/subscriptions/entities/setup"
echo ""
echo "=========================================="
echo "✅ Diagnóstico completado!"
echo "=========================================="