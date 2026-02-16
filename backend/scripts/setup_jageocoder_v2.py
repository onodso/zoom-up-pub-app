import os
import shutil
import subprocess
import time

# Config
DB_DIR = "/app/data/jageocoder_db"
DICT_URL = "https://www.info-proto.com/static/jageocoder/20250423/v2/jukyo_all_20250423_v22.zip"
ZIP_FILE = "jukyo_all_20250423_v22.zip"

def run_command(cmd):
    print(f"Exec: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def reinstall_jageocoder():
    print("🚀 Starting jageocoder Dictionary Re-installation (CLI Wrapper)...")
    
    # 1. Clean existing DB
    if os.path.exists(DB_DIR):
        print(f"🗑️  Removing existing DB at {DB_DIR}...")
        try:
             shutil.rmtree(DB_DIR)
        except Exception as e:
             print(f"Warning: Could not remove dir: {e}")
    
    os.makedirs(DB_DIR, exist_ok=True)
    
    # 2. Download Dictionary
    # We download to a temp location or current dir
    if not os.path.exists(ZIP_FILE):
        print(f"⬇️  Downloading {DICT_URL}...")
        try:
            run_command(["jageocoder", "download-dictionary", DICT_URL])
        except subprocess.CalledProcessError:
             print("❌ Download failed. Creating empty marker to prevent loop.")
             return

    if not os.path.exists(ZIP_FILE):
        print(f"❌ Zip file {ZIP_FILE} not found after download.")
        return

    # 3. Install Dictionary
    print("📦 Installing Dictionary...")
    # jageocoder install-dictionary [-d] [-y] [--db-dir=<dir>] <path>
    run_command(["jageocoder", "install-dictionary", "-y", "--db-dir", DB_DIR, ZIP_FILE])
    
    print("✅ Dictionary Installation Completed via CLI!")
    
    # 4. Verify (using python check)
    print("🔍 Verifying via Python API...")
    try:
        import jageocoder
        jageocoder.init(db_dir=DB_DIR)
        res = jageocoder.searchNode("北海道札幌市中央区北1条西2丁目")
        if res and len(res) > 0:
            print(f"✅ Search Test Passed: {len(res)} results found.")
        else:
            print("❌ Search Test Failed (Zero results).")
    except Exception as e:
        print(f"Warning: Verification threw error: {e}")

if __name__ == "__main__":
    reinstall_jageocoder()
