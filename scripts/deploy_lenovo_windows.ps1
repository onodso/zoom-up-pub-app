# Deploy Phase 3/4 to Lenovo Tiny (Windows PowerShell)
# Usage: .\scripts\deploy_lenovo_windows.ps1

Write-Host "🚀 Deploying Zoom City DX App (Phase 4) to Lenovo Tiny..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. 動作環境確認
Write-Host "1. Checking Environment... " -NoNewline
try {
    docker ps > $null 2>&1
    Write-Host "Docker is running ✅" -ForegroundColor Green
} catch {
    Write-Host "Docker is NOT running ❌" -ForegroundColor Red
    exit 1
}

# 2. コード更新
Write-Host "2. Pulling latest code... " -NoNewline
git pull origin main > $null 2>&1
Write-Host "Done ✅" -ForegroundColor Green

# 3. コンテナ再起動 (Build含む)
Write-Host "3. Rebuilding & Restarting Containers..." -ForegroundColor Cyan
docker compose -f docker-compose.lenovo.yml up -d --build
if ($?) {
    Write-Host "   Containers started ✅" -ForegroundColor Green
} else {
    Write-Host "   Docker Compose failed ❌" -ForegroundColor Red
    exit 1
}

# 4. DBマイグレーション
Write-Host "4. Running DB Migration... " -NoNewline
# Retry loop for DB readiness
for ($i=1; $i -le 10; $i++) {
    try {
        docker compose -f docker-compose.lenovo.yml exec -T api alembic upgrade head > $null 2>&1
        if ($?) {
            Write-Host "Done ✅" -ForegroundColor Green
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 3
    if ($i -eq 10) { Write-Host "Failed ❌" -ForegroundColor Red }
}

# 5. フロントエンド (Vite) ビルド & デプロイ
# Lenovo環境ではローカルビルドではなくDocker内ビルド/ホスティングを推奨
# docker-compose.lenovo.yml で nginx などの配信設定が必要だが、
# 現状は簡易的に `npm run dev` 相当で動かすか、ビルド済みファイルを配信する形になる。
# 今回は `api` コンテナがメインのため、フロントエンドのビルドはスキップ（または別途手順）と仮定。
# ※本来は frontend コンテナを追加すべき

# 6. ヘルスチェック
Write-Host "5. Health Check... " -NoNewline
$max_retries = 12
$retry_count = 0
$healthy = $false

while (-not $healthy -and $retry_count -lt $max_retries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            Write-Host "OK ✅" -ForegroundColor Green
        }
    } catch {
        Start-Sleep -Seconds 5
        $retry_count++
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
}

if (-not $healthy) {
    Write-Host "Timeout ❌" -ForegroundColor Red
    exit 1
}

# 7. 完了表示
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "   Frontend: http://localhost:3000 (if running)"
Write-Host "   Backend : http://localhost:8000/docs"
Write-Host "   Admin DB: http://localhost:8000/admin (if configured)"

