import tkinter as tk
from tkinter import filedialog, messagebox
import os
import requests
import hashlib
import shutil
import sys
import subprocess
import platform
import logging
import time

# Configure logging to append
logging.basicConfig(filename='necroforge_update.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

class NecroForgeApp:
    VERSION = "1.0.4"  # Incremented to differentiate from previous versions
    UPDATE_URL ="https://raw.githubusercontent.com/asasinsqrl/NecroForge/main/necroforge.py"
    TEMPLATE_URL = "https://github.com/wowte/NecroForge/raw/main/templates.json"
    CURRENT_FILE = os.path.abspath(__file__)

    def __init__(self, root):
        self.root = root
        self.root.title("NecroForge")
        self.root.geometry("550x420")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(self.main_frame, text=f"NecroForge v{self.VERSION}", font=("Arial", 12, "bold"), fg="#4CAF50").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        tk.Button(self.main_frame, text="Check for Updates", command=self.check_for_updates, width=15, font=("Arial", 10)).grid(row=0, column=1, pady=5, sticky="e")

        tk.Label(self.main_frame, text="Select Input .txt File:", font=("Arial", 12)).grid(row=1, column=0, columnspan=2, pady=10, sticky="w")
        self.file_path_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.file_path_var, width=50).grid(row=2, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_file, width=10).grid(row=2, column=1, pady=5, padx=5)

        tk.Label(self.main_frame, text="Output Directory:", font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10, sticky="w")
        self.output_dir_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.output_dir_var, width=50).grid(row=4, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_output_dir, width=10).grid(row=4, column=1, pady=5, padx=5)

        tk.Label(self.main_frame, text="Output Folder Name (optional):", font=("Arial", 12)).grid(row=5, column=0, columnspan=2, pady=10, sticky="w")
        self.folder_name_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.folder_name_var, width=50).grid(row=6, column=0, pady=5, padx=5)
        tk.Label(self.main_frame, text="Leave blank to use input file name", font=("Arial", 10, "italic")).grid(row=7, column=0, columnspan=2, pady=2, sticky="w")

        self.use_templates_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.main_frame,
            text="Use default templates for index.html, style.css, script.js",
            variable=self.use_templates_var,
            font=("Arial", 10)
        ).grid(row=8, column=0, columnspan=2, pady=5, sticky="w")

        self.generate_button = tk.Button(
            self.main_frame,
            text="Generate Files",
            command=self.generate_files,
            width=20,
            height=2,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        self.generate_button.grid(row=9, column=0, columnspan=2, pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path_var.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.folder_name_var.set(base_name)

    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_var.set(output_dir)

    def check_write_permissions(self, path):
        directory = os.path.dirname(path)
        return os.access(directory, os.W_OK)

    def is_frozen(self):
        return getattr(sys, 'frozen', False)

    def check_for_updates(self):
        if self.is_frozen():
            msg = "Updates are not supported when running as a frozen executable."
            logging.error(msg)
            messagebox.showinfo("Update", msg)
            return

        if not self.check_write_permissions(self.CURRENT_FILE):
            msg = f"No write permission for {os.path.dirname(self.CURRENT_FILE)}."
            logging.error(msg)
            messagebox.showerror("Update Error", msg)
            return

        temp_path = os.path.join(os.path.dirname(self.CURRENT_FILE), "necroforge_tmp.py")
        batch_path = os.path.join(os.path.dirname(self.CURRENT_FILE), "update.bat")
        shell_path = os.path.join(os.path.dirname(self.CURRENT_FILE), "update.sh")

        logging.info(f"Starting update check. UPDATE_URL: {self.UPDATE_URL}")
        logging.info(f"Temp path: {temp_path}, Batch path: {batch_path}")

        try:
            # Clean up existing temporary files
            for path in [temp_path, batch_path, shell_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        logging.info(f"Cleaned up existing file: {path}")
                    except Exception as e:
                        logging.warning(f"Failed to clean up {path}: {str(e)}")

            # Fetch the latest script
            logging.info("Fetching latest script...")
            response = requests.get(self.UPDATE_URL, timeout=5)
            response.raise_for_status()
            latest_content = response.text
            logging.info("Latest script fetched successfully.")

            # Compute SHA-256 hashes for comparison
            logging.info("Computing hashes...")
            with open(self.CURRENT_FILE, 'r', encoding='utf-8') as f:
                local_content = f.read()
                local_hash = hashlib.sha256(local_content.encode('utf-8')).hexdigest()
            latest_hash = hashlib.sha256(latest_content.encode('utf-8')).hexdigest()
            logging.info(f"Local hash: {local_hash}, Latest hash: {latest_hash}")

            if local_hash != latest_hash:
                if not messagebox.askyesno("Update Available", "A new version of NecroForge is available. Update now?"):
                    logging.info("Update cancelled by user.")
                    return

                # Write the new script to a temporary file
                logging.info(f"Writing new script to {temp_path}...")
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(latest_content)
                time.sleep(0.5)  # Ensure file is written
                logging.info(f"Temporary file written: {temp_path}")

                # Verify temp file exists
                if not os.path.exists(temp_path):
                    msg = f"Update failed: Temporary file {temp_path} was not created."
                    logging.error(msg)
                    messagebox.showerror("Update Error", msg)
                    return

                # Platform-specific update script
                if platform.system() == "Windows":
                    batch_content = f"""@echo off
echo Updating NecroForge...
ping 127.0.0.1 -n 10 >nul
move /Y "{temp_path}" "{self.CURRENT_FILE}" || (
    echo Failed to replace {self.CURRENT_FILE}
    exit /b 1
)
echo Replaced {self.CURRENT_FILE}
del "{temp_path}" || (
    echo Could Not Find {temp_path}
)
echo Deleted temporary file
start "" "{sys.executable}" "{self.CURRENT_FILE}" --updated
echo Restarted application
exit
"""
                    logging.info(f"Writing batch file to {batch_path}...")
                    with open(batch_path, 'w', encoding='utf-8') as batch_file:
                        batch_file.write(batch_content)
                    time.sleep(0.5)  # Ensure file is written
                    logging.info(f"Batch file written: {batch_path}")
                    if not os.path.exists(batch_path):
                        msg = f"Update failed: Batch file {batch_path} was not created."
                        logging.error(msg)
                        messagebox.showerror("Update Error", msg)
                        return
                    logging.info(f"Executing batch file: {batch_path}")
                    subprocess.Popen(['cmd', '/c', batch_path], shell=True)
                    time.sleep(7)  # Increased delay for file operations
                else:
                    shell_content = f"""#!/bin/bash
sleep 7
mv "{temp_path}" "{self.CURRENT_FILE}" || exit 1
rm "{temp_path}" || true
"{sys.executable}" "{self.CURRENT_FILE}" --updated &
rm "{shell_path}" || true
"""
                    logging.info(f"Writing shell script to {shell_path}...")
                    with open(shell_path, 'w', encoding='utf-8') as shell_file:
                        shell_file.write(shell_content)
                    os.chmod(shell_path, 0o755)
                    logging.info(f"Executing shell script: {shell_path}")
                    subprocess.Popen([shell_path], shell=True)
                    time.sleep(7)

                logging.info("Update initiated, closing application...")
                self.root.destroy()  # Cleaner exit
            else:
                logging.info("No update needed, hashes match.")
                messagebox.showinfo("Update", "NecroForge is up to date.")
        except requests.RequestException as e:
            msg = f"Update failed: Network error while fetching update ({str(e)})."
            logging.error(msg)
            messagebox.showerror("Update Error", msg)
        except PermissionError as e:
            msg = f"Update failed: Insufficient permissions to write to {temp_path} or {self.CURRENT_FILE} ({str(e)})."
            logging.error(msg)
            messagebox.showerror("Update Error", msg)
        except Exception as e:
            msg = f"Update failed: {str(e)}"
            logging.error(msg, exc_info=True)
            messagebox.showerror("Update Error", msg)

    def generate_files(self):
        input_file = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        folder_name = self.folder_name_var.get()
        use_templates = self.use_templates_var.get()

        if not input_file or not output_dir:
            messagebox.showerror("Error", "Please select both an input file and output directory.")
            return

        if not folder_name:
            folder_name = os.path.splitext(os.path.basename(input_file))[0]

        output_path = os.path.join(output_dir, folder_name)
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder: {str(e)}")
            return

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = [line.rstrip() for line in f]

            templates = {
                'index.html': '<html><head><title>{title}</title></head><body>{content}</body></html>',
                'style.css': 'body {{ font-family: Arial, sans-serif; }}',
                'script.js': 'console.log("Generated by Necromancer");'
            }

            for line in lines:
                if line:
                    parts = line.split(',', 1)
                    if len(parts) < 2:
                        messagebox.showerror("Error", f"Invalid format in line: {line} (missing comma-separated content)")
                        return
                    file_name, content = parts[0].strip(), parts[1].strip()
                    if not os.path.basename(file_name):
                        messagebox.showerror("Error", f"Invalid file name in line: {line}")
                        return
                    file_path = os.path.join(output_path, file_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    print(f"Processing: {file_name} -> {content[:50]}...")
                    print(f"Writing to: {file_path}")

                    try:
                        if use_templates and file_name in templates:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(templates[file_name].format(title=file_name, content=content))
                        else:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to write {file_name}: {str(e)}")
                        return

            if all(os.path.exists(os.path.join(output_path, f)) for f in ['index.html', 'css/style.css', 'js/script.js', 'readme.md']):
                messagebox.showinfo("Success", f"Files generated in {output_path}")
            else:
                messagebox.showerror("Error", f"Some files were not generated in {output_path}")

        except UnicodeDecodeError as e:
            messagebox.showerror("Error", f"Failed to read input file: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate files: {str(e)}")

if __name__ == "__main__":
    # Clean up stale batch/shell files from previous updates
    for path in ["update.bat", "update.sh", "necroforge_tmp.py"]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logging.info(f"Cleaned up stale file: {path}")
            except Exception as e:
                logging.warning(f"Failed to clean up stale file {path}: {str(e)}")

    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        temp_file = os.path.join(os.path.dirname(NecroForgeApp.CURRENT_FILE), "necroforge_tmp.py")
        try:
            if not os.path.exists(temp_file):
                msg = f"Update failed: Temporary file {temp_file} not found."
                print(msg)
                logging.error(msg)
                sys.exit(1)
            shutil.move(temp_file, NecroForgeApp.CURRENT_FILE)
            msg = "NecroForge updated. Please restart the application."
            print(msg)
            logging.info(msg)
            # Restart the application without the --update flag
            subprocess.Popen([sys.executable, NecroForgeApp.CURRENT_FILE])
            sys.exit(0)
        except PermissionError as e:
            msg = f"Update failed: Insufficient permissions to overwrite {NecroForgeApp.CURRENT_FILE} ({str(e)})."
            print(msg)
            logging.error(msg)
            sys.exit(1)
        except Exception as e:
            msg = f"Update failed: {str(e)}"
            print(msg)
            logging.error(msg)
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--updated":
        messagebox.showinfo("Update", f"NecroForge updated to v{NecroForgeApp.VERSION}.")
        root = tk.Tk()
        app = NecroForgeApp(root)
        root.mainloop()
    else:
        root = tk.Tk()
        app = NecroForgeApp(root)
        root.mainloop()