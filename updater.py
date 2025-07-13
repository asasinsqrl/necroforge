import requests
import hashlib
import os
import shutil
import sys
import subprocess
import platform

UPDATE_URL = "https://github.com/asasinsqrl/NecroForge/raw/main/necroforge.py"
CURRENT_FILE = os.path.abspath(__file__)  # Reference the script file, not the executable

def update_necroforge():
    try:
        # Fetch the latest script
        response = requests.get(UPDATE_URL, timeout=5)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes
        latest_content = response.text

        # Compute SHA-256 hashes for comparison
        with open(CURRENT_FILE, 'rb') as f:
            local_hash = hashlib.sha256(f.read()).hexdigest()
        latest_hash = hashlib.sha256(latest_content.encode('utf-8')).hexdigest()

        if local_hash != latest_hash:
            # Write the new script to a temporary file
            temp_path = os.path.join(os.path.dirname(CURRENT_FILE), "necroforge_tmp.py")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(latest_content)

            # Platform-specific update script
            if platform.system() == "Windows":
                # Create a batch file to handle the update
                batch_content = f"""@echo off
ping 127.0.0.1 -n 3 >nul
move /Y "{temp_path}" "{CURRENT_FILE}"
start "" "{sys.executable}" "{CURRENT_FILE}"
exit"""
                batch_path = os.path.join(os.path.dirname(CURRENT_FILE), "update.bat")
                with open(batch_path, 'w', encoding='utf-8') as batch_file:
                    batch_file.write(batch_content)
                subprocess.Popen([batch_path], shell=True)
            else:
                # Create a shell script for Unix-like systems
                shell_content = f"""#!/bin/bash
sleep 2
mv "{temp_path}" "{CURRENT_FILE}"
"{sys.executable}" "{CURRENT_FILE}" &
"""
                shell_path = os.path.join(os.path.dirname(CURRENT_FILE), "update.sh")
                with open(shell_path, 'w', encoding='utf-8') as shell_file:
                    shell_file.write(shell_content)
                os.chmod(shell_path, 0o755)  # Make the shell script executable
                subprocess.Popen([shell_path], shell=True)

            sys.exit(0)
        else:
            print("NecroForge is up to date.")
    except requests.RequestException as e:
        print(f"Update failed: Network error while fetching update ({str(e)}).")
    except PermissionError:
        print(f"Update failed: Insufficient permissions to write to {temp_path} or {CURRENT_FILE}.")
    except Exception as e:
        print(f"Update failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        try:
            # Move the temporary file to replace the current script
            temp_file = os.path.join(os.path.dirname(sys.argv[0]), "necroforge_tmp.py")
            shutil.move(temp_file, CURRENT_FILE)
            print("NecroForge updated. Please restart the application.")
        except PermissionError:
            print(f"Update failed: Insufficient permissions to overwrite {CURRENT_FILE}.")
        except FileNotFoundError:
            print(f"Update failed: Temporary file {temp_file} not found.")
        except Exception as e:
            print(f"Update failed: {str(e)}")
    else:
        update_necroforge()