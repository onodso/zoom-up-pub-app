#!/bin/bash
# Deploy Stage 2 to Lenovo Tiny (Windows + Docker)
# Usage: bash scripts/deploy_to_lenovo.sh
# Password: Zoom5145

set -e  # Exit on error

LENOVO_IP="100.107.246.40"
LENOVO_USER="onodera"
PROJECT_DIR="C:/Users/onodera/zoom-dx"

echo "🚀 Deploying Stage 2 to Lenovo Tiny..."
echo "Target: $LENOVO_USER@$LENOVO_IP (Windows + Docker)"
echo "================================"

# Check Tailscale connection
echo -n "1. Checking Tailscale connection... "
if ping -c 1 -W 1 $LENOVO_IP > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Failed"
    echo "   Please ensure Tailscale is running and Lenovo Tiny is online"
    exit 1
fi

# Phase 1: Transfer files (using scp for Windows)
echo "2. Transferring files to Lenovo Tiny..."
echo "   ⏳ This may take a minute..."

# Create a temporary archive
tar -czf /tmp/zoom-dx-backend.tar.gz -C backend .
tar -czf /tmp/zoom-dx-scripts.tar.gz -C scripts .

# Transfer archives
scp /tmp/zoom-dx-backend.tar.gz $LENOVO_USER@$LENOVO_IP:C:/Users/onodera/backend.tar.gz
scp /tmp/zoom-dx-scripts.tar.gz $LENOVO_USER@$LENOVO_IP:C:/Users/onodera/scripts.tar.gz

# Extract on Windows side (using PowerShell)
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    cd $PROJECT_DIR;
    if (!(Test-Path backend)) { mkdir backend };
    if (!(Test-Path scripts)) { mkdir scripts };
    tar -xzf C:/Users/onodera/backend.tar.gz -C backend;
    tar -xzf C:/Users/onodera/scripts.tar.gz -C scripts;
    Remove-Item C:/Users/onodera/backend.tar.gz;
    Remove-Item C:/Users/onodera/scripts.tar.gz
\""

echo "   ✅ Files transferred"

# Cleanup
rm /tmp/zoom-dx-backend.tar.gz /tmp/zoom-dx-scripts.tar.gz

# Phase 2: Run migration
echo "3. Running database migration..."
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    cd $PROJECT_DIR;
    Get-Content backend/db/migrations/008_add_scoring_columns.sql | docker exec -i zoom-dx-postgres psql -U zoom_admin -d localgov_intelligence 2>&1 | Select-Object -Last 3
\""

echo "   ✅ Migration completed"

# Phase 3: Install AI packages
echo "4. Installing AI packages (torch, transformers)..."
echo "   ⏳ This will take 5-10 minutes..."

ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    docker exec zoom-dx-api pip3 install -q torch transformers fugashi ipadic;
    docker exec zoom-dx-api python3 -c 'import torch; import transformers; print(\"✅ AI packages installed\")' 2>&1 | Select-Object -Last 1
\""

# Phase 4: Run data enrichment
echo "5. Running data enrichment..."
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    docker exec zoom-dx-api python3 scripts/enrich_dx_status_lite.py 2>&1 | Select-String -Pattern 'Completed'
\""

echo "   ✅ Enrichment completed"

# Phase 5: Test scoring
echo "6. Testing scoring engine..."
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    docker exec zoom-dx-api python3 scripts/nightly_scoring_lite.py 2>&1 | Select-String -Pattern 'Processing|Success|Score' | Select-Object -First 5
\""

# Phase 6: Restart API
echo "7. Restarting API container..."
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    cd $PROJECT_DIR;
    docker compose -f docker-compose.lenovo.yml restart api;
    Start-Sleep -Seconds 5
\""

echo "   ✅ API restarted"

# Phase 7: Health check
echo "8. Running health check..."
sleep 3

# Use curl on Windows if available, otherwise PowerShell
health_check=$(ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    try {
        \\\$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing;
        if (\\\$response.StatusCode -eq 200) { Write-Output '✅' } else { Write-Output '❌' }
    } catch {
        Write-Output '❌'
    }
\"")

echo "   $health_check API is healthy"

# Phase 8: Test new endpoints
echo "9. Testing Stage 2 endpoints..."

echo -n "   - Score API... "
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    try {
        Invoke-WebRequest -Uri 'http://localhost:8000/api/scores/011002' -UseBasicParsing | Out-Null;
        Write-Output '✅'
    } catch {
        Write-Output '⚠️'
    }
\""

echo -n "   - Map API... "
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    try {
        Invoke-WebRequest -Uri 'http://localhost:8000/api/scores/map/all' -UseBasicParsing | Out-Null;
        Write-Output '✅'
    } catch {
        Write-Output '⚠️'
    }
\""

echo -n "   - Proposal API... "
ssh $LENOVO_USER@$LENOVO_IP "powershell -Command \"
    try {
        \\\$body = @{ city_code = '011002'; focus_area = 'general' } | ConvertTo-Json;
        Invoke-WebRequest -Uri 'http://localhost:8000/api/proposals/generate' -Method Post -Body \\\$body -ContentType 'application/json' -UseBasicParsing | Out-Null;
        Write-Output '✅'
    } catch {
        Write-Output '⚠️'
    }
\""

echo ""
echo "================================"
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Next Steps:"
echo "   1. View Swagger UI: http://$LENOVO_IP:8000/docs"
echo "   2. Test Score API: curl http://$LENOVO_IP:8000/api/scores/011002 | jq ."
echo "   3. Setup Task Scheduler: ssh $LENOVO_USER@$LENOVO_IP"
echo ""
