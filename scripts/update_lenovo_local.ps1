# ========================================
# Lenovo Tiny Local Update Script
# ========================================
# Run this script DIRECTLY on Lenovo Tiny (Windows PowerShell)
# Right-click PowerShell -> Run as Administrator
#
# このスクリプトをLenovo Tiny上で直接実行してください

$ErrorActionPreference = "Stop"

Write-Host "🔧 Lenovo Tiny - Stage 2 Database Fix" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "1. Checking Docker status..." -NoNewline
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}
Write-Host " ✅" -ForegroundColor Green

# Navigate to project directory
$PROJECT_DIR = "C:\Users\onodera\zoom-dx"
if (-not (Test-Path $PROJECT_DIR)) {
    Write-Host "❌ Project directory not found: $PROJECT_DIR" -ForegroundColor Red
    exit 1
}

Set-Location $PROJECT_DIR
Write-Host "2. Project directory: $PROJECT_DIR ✅" -ForegroundColor Green

# Check current database name
Write-Host ""
Write-Host "3. Checking current database configuration..." -ForegroundColor Yellow
$dbName = docker exec zoom-dx-postgres psql -U zoom_admin -t -c "SELECT datname FROM pg_database WHERE datname NOT IN ('postgres', 'template0', 'template1');"
Write-Host "   Current databases: $($dbName.Trim())" -ForegroundColor Cyan

# Check if zoom_dx_db exists
$hasZoomDb = docker exec zoom-dx-postgres psql -U zoom_admin -t -c "SELECT 1 FROM pg_database WHERE datname = 'zoom_dx_db';" 2>$null
if ($hasZoomDb -match "1") {
    Write-Host "   ✅ Database 'zoom_dx_db' exists" -ForegroundColor Green
    $DB_NAME = "zoom_dx_db"
} else {
    Write-Host "   ⚠️  Database 'zoom_dx_db' not found" -ForegroundColor Yellow
    Write-Host "   Creating database..." -NoNewline
    docker exec zoom-dx-postgres psql -U zoom_admin -c "CREATE DATABASE zoom_dx_db;" 2>&1 | Out-Null
    Write-Host " ✅" -ForegroundColor Green
    $DB_NAME = "zoom_dx_db"
}

# Update .env file
Write-Host ""
Write-Host "4. Updating .env file..." -NoNewline
$envContent = @"
# Database Configuration (Updated $(Get-Date -Format 'yyyy-MM-dd HH:mm'))
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=zoom_admin
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=$DB_NAME

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=e9bzZlPen+O8srWPNHaql1dUVlgqwi3tek921quPLyA=
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_URL=http://localhost:11434

# APIs
ESTAT_APP_ID=ffaf6bbba7989e72e39d796fd0f62977d42e5731
GOOGLE_SEARCH_API_KEY=***REMOVED***
GOOGLE_SEARCH_ENGINE_ID=a1e07736bef784a0c

# CORS
ALLOWED_ORIGINS=*

# Environment
NODE_ENV=production
LOG_LEVEL=INFO
"@

$envContent | Out-File -FilePath "$PROJECT_DIR\.env" -Encoding UTF8 -Force
Write-Host " ✅" -ForegroundColor Green

# Rebuild and restart API container
Write-Host ""
Write-Host "5. Rebuilding API container..." -ForegroundColor Yellow
Write-Host "   (This may take 2-3 minutes)" -ForegroundColor Gray

docker-compose -f docker-compose.lenovo.yml build api 2>&1 | Select-String "Step|Successfully"

Write-Host ""
Write-Host "6. Restarting containers..." -NoNewline
docker-compose -f docker-compose.lenovo.yml down 2>&1 | Out-Null
Start-Sleep -Seconds 3
docker-compose -f docker-compose.lenovo.yml up -d 2>&1 | Out-Null
Start-Sleep -Seconds 10
Write-Host " ✅" -ForegroundColor Green

# Check container health
Write-Host ""
Write-Host "7. Checking container status..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "zoom-dx"

# Test database connection
Write-Host ""
Write-Host "8. Testing database connection..." -NoNewline
$dbTest = docker exec zoom-dx-api python3 -c "from backend.config import settings; print(f'DB: {settings.DB_NAME}')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "   $dbTest" -ForegroundColor Cyan
} else {
    Write-Host " ⚠️" -ForegroundColor Yellow
    Write-Host "   $dbTest" -ForegroundColor Red
}

# Test API health
Write-Host ""
Write-Host "9. Testing API health..." -NoNewline
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "   API is responding!" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Checking API logs:" -ForegroundColor Yellow
    docker logs zoom-dx-api --tail 20
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Update Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Check Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   2. Check logs: docker logs zoom-dx-api -f" -ForegroundColor White
Write-Host ""
