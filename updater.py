import requests
import hashlib
import os

UPDATE_URL = "https://github.com/asasinsqrl/necroforge/raw/main/necroforge.py"  # Replace with your URL
CURRENT_FILE = "necroforge.py"

def update_necroforge():
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        if response.status_code == 200:
            latest_content = response.text
            local_hash = hashlib.md5(open(CURRENT_FILE, 'rb').read()).hexdigest()
            latest_hash = hashlib.md5(latest_content.encode()).hexdigest()
            if local_hash != latest_hash:
                with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
                    f.write(latest_content)
                print("NecroForge updated. Please restart the application.")
            else:
                print("NecroForge is up to date.")
    except Exception as e:
        print(f"Update failed: {str(e)}")

if __name__ == "__main__":
    update_necroforge()