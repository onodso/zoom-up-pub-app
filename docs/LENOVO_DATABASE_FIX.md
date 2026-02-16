# Lenovo Tiny Database Configuration Fix

**Date**: 2026-02-13
**Issue**: API container failing with "FATAL: database does not exist"
**Root Cause**: Database name mismatch between config.py and Docker configuration

---

## 🔍 Problem Analysis

The screenshot showed Docker containers running but API logs showing database connection errors:
```
FATAL: database 'zoom_admin' does not exist
```

### Root Causes Found:
1. **config.py** had default DB_NAME = "localgov_intelligence"
2. **docker-compose.lenovo.yml** creates database "zoom_dx_db"
3. **Pydantic Settings** wasn't reading POSTGRES_* environment variables correctly
4. Environment variable mismatch causing connection to fail

---

## ✅ Changes Made

### 1. Fixed `backend/config.py`
**Changed from:**
```python
DB_NAME: str = Field("localgov_intelligence", validation_alias="postgres_db")
```

**Changed to:**
```python
DB_NAME: str = os.getenv("POSTGRES_DB", "zoom_dx_db")
```

Now correctly reads from POSTGRES_DB environment variable with proper default.

### 2. Updated `docker-compose.lenovo.yml`
- Added `env_file: .env` to API service
- Added explicit environment variable mappings
- Ensured POSTGRES_DB is consistently set to "zoom_dx_db"

---

## 🚀 How to Apply Fix

### **Option A: Transfer Files via USB/Network Share** (Recommended if SSH fails)

1. **On Mac**: Copy these files to USB drive or network share:
   ```bash
   # Files to copy:
   - backend/config.py
   - docker-compose.lenovo.yml
   - scripts/update_lenovo_local.ps1
   ```

2. **On Lenovo Tiny**:
   - Insert USB or access network share
   - Copy files to `C:\Users\onodera\zoom-dx\` (overwrite existing)
   - Open PowerShell as Administrator
   - Run:
     ```powershell
     cd C:\Users\onodera\zoom-dx
     .\scripts\update_lenovo_local.ps1
     ```

### **Option B: Manual File Edit** (Quick but manual)

**On Lenovo Tiny**, edit files directly:

1. **Edit `C:\Users\onodera\zoom-dx\backend\config.py`**:
   Find line ~11 and change:
   ```python
   # OLD:
   DB_NAME: str = Field("localgov_intelligence", validation_alias="postgres_db")

   # NEW:
   DB_NAME: str = os.getenv("POSTGRES_DB", "zoom_dx_db")
   ```

2. **Check database exists**:
   ```powershell
   docker exec zoom-dx-postgres psql -U zoom_admin -c "\l"
   ```

   If "zoom_dx_db" doesn't exist, create it:
   ```powershell
   docker exec zoom-dx-postgres psql -U zoom_admin -c "CREATE DATABASE zoom_dx_db;"
   ```

3. **Restart API container**:
   ```powershell
   cd C:\Users\onodera\zoom-dx
   docker-compose -f docker-compose.lenovo.yml restart api

   # Wait 10 seconds, then check health
   Start-Sleep 10
   curl http://localhost:8000/api/health
   ```

### **Option C: Use Remote PowerShell** (If SSH works)

From Mac:
```bash
ssh onodera@100.107.246.40 "powershell -ExecutionPolicy Bypass -File C:/Users/onodera/zoom-dx/scripts/update_lenovo_local.ps1"
```

---

## 🧪 Verification Steps

After applying the fix, verify everything works:

### 1. Check API Health
```powershell
curl http://localhost:8000/api/health
# Expected: {"status":"ok","version":"1.0.0"}
```

### 2. Check Database Connection
```powershell
docker exec zoom-dx-api python3 -c "from backend.config import settings; print(f'DB: {settings.DB_NAME}')"
# Expected: DB: zoom_dx_db
```

### 3. Check API Logs
```powershell
docker logs zoom-dx-api --tail 50
# Should NOT see "FATAL: database does not exist"
```

### 4. Test Score API
```powershell
curl http://localhost:8000/api/scores/011002
# Should return JSON data (or 404 if no data yet)
```

---

## 📊 Expected Outcome

After fix:
- ✅ API container starts without database errors
- ✅ `/api/health` returns 200 OK
- ✅ Swagger UI accessible at http://localhost:8000/docs
- ✅ All containers running: postgres, api, redis, ollama, node-red

---

## 🔧 Troubleshooting

### Issue: API still shows database errors
**Solution**: Check .env file has correct POSTGRES_DB value:
```powershell
cat C:\Users\onodera\zoom-dx\.env | Select-String "POSTGRES_DB"
# Should show: POSTGRES_DB=zoom_dx_db
```

### Issue: Database doesn't exist
**Solution**: Create it manually:
```powershell
docker exec zoom-dx-postgres psql -U zoom_admin -c "CREATE DATABASE zoom_dx_db;"
```

### Issue: Permission denied
**Solution**: Run PowerShell as Administrator

---

## 📝 Next Steps After Fix

Once the database connection is working:

1. **Run Database Migration**:
   ```powershell
   docker exec zoom-dx-api python3 -c "
   import psycopg2
   from backend.config import settings
   conn = psycopg2.connect(
       host=settings.DB_HOST,
       database=settings.DB_NAME,
       user=settings.DB_USER,
       password=settings.DB_PASSWORD
   )
   print('✅ Connection successful!')
   conn.close()
   "
   ```

2. **Run Migration 008** (if needed):
   ```powershell
   docker exec zoom-dx-api bash -c "cat backend/db/migrations/008_add_scoring_columns.sql | psql postgresql://zoom_admin:your_password@postgres:5432/zoom_dx_db"
   ```

3. **Continue with Stage 2 Deployment**:
   - Follow `docs/LENOVO_TINY_STAGE2_DEPLOYMENT.md`
   - Install AI packages (torch, transformers)
   - Run data enrichment
   - Set up nightly scoring

---

**Questions?** Check Docker logs:
```powershell
docker logs zoom-dx-api -f
```
