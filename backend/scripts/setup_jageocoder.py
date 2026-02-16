import jageocoder
import os
import sys
import requests
import subprocess
import shutil

# Dictionary directory (persistent volume recommended)
# Mapped to ./data on host
DATA_DIR = "/app/data"
DICT_DIR = os.path.join(DATA_DIR, "jageocoder_db")
DICT_URL = "https://www.info-proto.com/static/jageocoder/latest/jukyo_all_v21.zip"
ZIP_PATH = os.path.join(DATA_DIR, "jukyo_all_v21.zip")

def setup_dictionary():
    if not os.path.exists(DICT_DIR):
        os.makedirs(DICT_DIR, exist_ok=True)
    
    print(f"📦 Checking jageocoder dictionary in {DICT_DIR}...")
    
    # Check if already installed (try to init)
    try:
        jageocoder.init(db_dir=DICT_DIR)
        print("✅ Dictionary ID found. Verifying...")
        # Simple verify by searching Tokyo
        try:
             res = jageocoder.searchNode("東京都新宿区西新宿2-8-1")
             if res:
                 print("✅ Dictionary verification success.")
                 return
        except:
             print("⚠️ Dictionary verification failed. Re-installing.")
    except:
        print("ℹ️ Dictionary not initialized.")

    # Download
    if not os.path.exists(ZIP_PATH):
        print(f"🚀 Downloading dictionary from {DICT_URL}...")
        print("   This may take a while (approx 2-3GB)...")
        try:
            with requests.get(DICT_URL, stream=True) as r:
                r.raise_for_status()
                with open(ZIP_PATH, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
            print("✅ Download complete.")
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return

    # Install
    print(f"📦 Installing dictionary to {DICT_DIR}...")
    try:
        cmd = ["jageocoder", "install-dictionary", ZIP_PATH, "--db-dir", DICT_DIR, "-y"]
        subprocess.run(cmd, check=True)
        print("✅ Installation complete.")
        
        # Cleanup
        # os.remove(ZIP_PATH) 
        print("ℹ️ Zip file kept for backup.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")

if __name__ == "__main__":
    setup_dictionary()

