import requests
import hashlib
import os
import shutil
import sys
import subprocess

UPDATE_URL = "https://github.com/asasinsqrl/NecroForge/raw/main/necroforge.py"
CURRENT_FILE = sys.executable

def update_necroforge():
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        if response.status_code == 200:
            latest_content = response.text
            local_hash = hashlib.md5(open(CURRENT_FILE, 'rb').read()).hexdigest()
            latest_hash = hashlib.md5(latest_content.encode()).hexdigest()
            if local_hash != latest_hash:
                temp_path = CURRENT_FILE + ".tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(latest_content)
                # Create a batch file to handle the move and restart
                batch_content = f'@echo off\nping 127.0.0.1 -n 2 >nul\nmove /Y "{temp_path}" "{CURRENT_FILE}"\nstart "" "{CURRENT_FILE}"\nexit'
                with open("update.bat", 'w') as batch_file:
                    batch_file.write(batch_content)
                subprocess.Popen(["update.bat"], shell=True)
                sys.exit(0)
            else:
                print("NecroForge is up to date.")
    except Exception as e:
        print(f"Update failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        try:
            shutil.move(sys.argv[0], CURRENT_FILE)
            print("NecroForge updated. Please restart the application.")
        except Exception as e:
            print(f"Update move failed: {str(e)}")
    else:
        update_necroforge()