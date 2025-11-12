# Script PowerShell dinámico para diagnosticar suscripciones con IP pública auto-detectada

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔧 Diagnóstico de Suscripciones Orion (AWS)" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

# Función para obtener IP pública
function Get-PublicIP {
    try {
        $ip = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5).Trim()
        return $ip
    } catch {
        Write-Host "⚠️ No se pudo obtener IP pública automáticamente" -ForegroundColor Yellow
        return $null
    }
}

# Obtener IP pública o solicitarla al usuario
$PUBLIC_IP = Get-PublicIP
if (-not $PUBLIC_IP) {
    $PUBLIC_IP = Read-Host "Ingresa la IP pública de tu instancia AWS"
}

Write-Host "🌐 Usando IP pública: $PUBLIC_IP" -ForegroundColor Green

# Variables
$ETL_SERVICE = "http://${PUBLIC_IP}:8080"
$ORION_URL = "http://${PUBLIC_IP}:1026"

Write-Host ""
Write-Host "🔗 URLs de servicios:" -ForegroundColor Cyan
Write-Host "   • ETL Service: $ETL_SERVICE" -ForegroundColor White
Write-Host "   • Orion Context Broker: $ORION_URL" -ForegroundColor White

Write-Host ""
Write-Host "1. 🔍 Verificando conectividad de servicios..." -ForegroundColor Green

# Verificar ETL Service
Write-Host "   • ETL Service:" -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "$ETL_SERVICE/etl" -Method Get -TimeoutSec 10
    Write-Host "     ✓ ETL Service accesible" -ForegroundColor Green
} catch {
    Write-Host "     ✗ ETL Service NO accesible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "     💡 Verifica que el puerto 8080 esté abierto en el Security Group" -ForegroundColor Yellow
}

# Verificar Orion Context Broker
Write-Host "   • Orion Context Broker:" -ForegroundColor White
try {
    $orionVersion = Invoke-RestMethod -Uri "$ORION_URL/version" -Method Get -TimeoutSec 10
    Write-Host "     ✓ Orion Context Broker accesible" -ForegroundColor Green
    Write-Host "     ℹ Versión: $($orionVersion.orion.version)" -ForegroundColor Cyan
} catch {
    Write-Host "     ✗ Orion Context Broker NO accesible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "     💡 Verifica que el puerto 1026 esté abierto en el Security Group" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "2. 📊 Health check del sistema de suscripciones..." -ForegroundColor Green
try {
    $healthCheck = Invoke-RestMethod -Uri "$ETL_SERVICE/subscriptions/health" -Method Get -TimeoutSec 10
    $healthCheck | ConvertTo-Json -Depth 10 | Write-Host
    
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✓ Sistema de suscripciones saludable" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Sistema de suscripciones con problemas" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Error obteniendo health check: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. 📋 Listando suscripciones..." -ForegroundColor Green
try {
    $subscriptions = Invoke-RestMethod -Uri "$ETL_SERVICE/subscriptions" -Method Get -TimeoutSec 10
    
    Write-Host "Con headers FIWARE: $($subscriptions.with_fiware_headers.total) suscripciones" -ForegroundColor Cyan
    Write-Host "Sin headers FIWARE: $($subscriptions.without_fiware_headers.total) suscripciones" -ForegroundColor Cyan
    
    $subscriptions | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "✗ Error listando suscripciones: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. 🏗️ Listando entidades..." -ForegroundColor Green
try {
    $entities = Invoke-RestMethod -Uri "$ETL_SERVICE/subscriptions/entities" -Method Get -TimeoutSec 10
    Write-Host "Total de entidades: $($entities.total_entities)" -ForegroundColor Cyan
    $entities | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "✗ Error listando entidades: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. 🔍 Consulta directa a Orion (con headers FIWARE)..." -ForegroundColor Green
try {
    $fiwareHeaders = @{
        "Accept" = "application/json"
        "Fiware-Service" = "smart"
        "Fiware-ServicePath" = "/"
    }
    $fiwareSubs = Invoke-RestMethod -Uri "$ORION_URL/v2/subscriptions" -Method Get -Headers $fiwareHeaders -TimeoutSec 10
    Write-Host "Suscripciones directas en Orion: $($fiwareSubs.Count)" -ForegroundColor Cyan
    $fiwareSubs | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "✗ Error en consulta directa con headers FIWARE: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "6. 🏗️ Consulta directa de entidades en Orion..." -ForegroundColor Green
try {
    $fiwareHeaders = @{
        "Accept" = "application/json"
        "Fiware-Service" = "smart"
        "Fiware-ServicePath" = "/"
    }
    $orionEntities = Invoke-RestMethod -Uri "$ORION_URL/v2/entities" -Method Get -Headers $fiwareHeaders -TimeoutSec 10
    Write-Host "Entidades directas en Orion: $($orionEntities.Count)" -ForegroundColor Cyan
    $orionEntities | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "✗ Error consultando entidades: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🛠️ Acciones de solución:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Si necesitas recrear suscripciones:" -ForegroundColor White
Write-Host "Invoke-RestMethod -Uri '$ETL_SERVICE/subscriptions/recreate' -Method Post" -ForegroundColor Yellow

Write-Host ""
Write-Host "Si necesitas recrear entidades:" -ForegroundColor White
Write-Host "Invoke-RestMethod -Uri '$ETL_SERVICE/subscriptions/entities/setup' -Method Post" -ForegroundColor Yellow

Write-Host ""
Write-Host "Para verificar logs del contenedor ETL:" -ForegroundColor White
Write-Host "sudo docker logs etl-service" -ForegroundColor Yellow

Write-Host ""
Write-Host "Para verificar puertos abiertos en Security Group:" -ForegroundColor White
Write-Host "- Puerto 1026 (Orion Context Broker)" -ForegroundColor Yellow
Write-Host "- Puerto 8080 (ETL Service)" -ForegroundColor Yellow
Write-Host "- Puerto 4200 (CrateDB - opcional para debug)" -ForegroundColor Yellow

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Diagnóstico completado!" -ForegroundColor Green
Write-Host "IP utilizada: $PUBLIC_IP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan