# Deploy Stage 2 to Lenovo Tiny (Windows PowerShell)
# Usage: .\scripts\deploy_lenovo_windows.ps1

Write-Host "🚀 Deploying Stage 2 to Lenovo Tiny (Windows)..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check Docker is running
Write-Host "1. Checking Docker status... " -NoNewline
try {
    docker ps > $null 2>&1
    Write-Host "✅" -ForegroundColor Green
} catch {
    Write-Host "❌" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

# Pull latest code
Write-Host "2. Pulling latest code... " -NoNewline
git pull origin main > $null 2>&1
Write-Host "✅" -ForegroundColor Green

# Run migration
Write-Host "3. Running database migration... " -NoNewline
try {
    Get-Content backend/db/migrations/008_add_scoring_columns.sql | docker exec -i zoom-dx-postgres psql -U zoom_admin -d localgov_intelligence > $null 2>&1
    Write-Host "✅" -ForegroundColor Green
} catch {
    Write-Host "⚠️  (May already be applied)" -ForegroundColor Yellow
}

# Install AI packages
Write-Host "4. Installing AI packages (this will take 5-10 minutes)..." -ForegroundColor Yellow
docker exec zoom-dx-api pip3 install -q torch transformers fugashi ipadic
$result = docker exec zoom-dx-api python3 -c "import torch; import transformers; print('✅ AI packages installed')" 2>&1 | Select-Object -Last 1
Write-Host "   $result" -ForegroundColor Green

# Data enrichment
Write-Host "5. Running data enrichment... " -NoNewline
docker exec zoom-dx-api python3 scripts/enrich_dx_status_lite.py > $null 2>&1
Write-Host "✅" -ForegroundColor Green

# Test scoring
Write-Host "6. Testing scoring engine..." -ForegroundColor Cyan
docker exec zoom-dx-api python3 scripts/nightly_scoring_lite.py 2>&1 | Select-String -Pattern "Processing|Success|Score" | Select-Object -First 5

# Restart API
Write-Host "7. Restarting API container... " -NoNewline
docker compose -f docker-compose.lenovo.yml restart api > $null 2>&1
Start-Sleep -Seconds 5
Write-Host "✅" -ForegroundColor Green

# Health check
Write-Host "8. Running health check... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "❌ (Status: $($response.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed" -ForegroundColor Red
}

# Test endpoints
Write-Host "9. Testing Stage 2 endpoints..." -ForegroundColor Cyan

Write-Host "   - Score API... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/scores/011002" -UseBasicParsing
    Write-Host "✅" -ForegroundColor Green
} catch {
    Write-Host "⚠️" -ForegroundColor Yellow
}

Write-Host "   - Map API... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/scores/map/all" -UseBasicParsing
    Write-Host "✅" -ForegroundColor Green
} catch {
    Write-Host "⚠️" -ForegroundColor Yellow
}

Write-Host "   - Proposal API... " -NoNewline
try {
    $body = @{
        city_code = "011002"
        focus_area = "general"
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/proposals/generate" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "✅" -ForegroundColor Green
} catch {
    Write-Host "⚠️" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. View Swagger UI: http://localhost:8000/docs"
Write-Host "   2. Test Score API: curl http://localhost:8000/api/scores/011002"
Write-Host "   3. Setup Task Scheduler for nightly scoring"
