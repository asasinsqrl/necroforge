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

# Configure logging
logging.basicConfig(filename='necroforge_update.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

class NecroForgeApp:
    VERSION = "1.0.5"
    UPDATE_URL = "https://api.github.com/repos/asasinsqrl/NecroForge/releases/latest"
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

    def check_for_updates(self):
        temp_exe = os.path.join(os.path.dirname(self.CURRENT_FILE), "necroforge_tmp.exe")
        batch_path = os.path.join(os.path.dirname(self.CURRENT_FILE), "update.bat")

        logging.info(f"Starting update check. UPDATE_URL: {self.UPDATE_URL}")
        try:
            # Clean up existing temporary files
            for path in [temp_exe, batch_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        logging.info(f"Cleaned up existing file: {path}")
                    except Exception as e:
                        logging.warning(f"Failed to clean up {path}: {str(e)}")

            # Check write permissions
            if not self.check_write_permissions(self.CURRENT_FILE):
                msg = f"No write permission for {os.path.dirname(self.CURRENT_FILE)}."
                logging.error(msg)
                messagebox.showerror("Update Error", msg)
                return

            # Fetch the latest release
            logging.info("Fetching latest release...")
            response = requests.get(self.UPDATE_URL, timeout=5)
            response.raise_for_status()
            release = response.json()
            latest_version = release['tag_name'].lstrip('v')  # e.g., "1.0.4"
            logging.info(f"Latest version: {latest_version}, Current version: {self.VERSION}")

            if latest_version != self.VERSION:
                if not messagebox.askyesno("Update Available", f"A new version ({latest_version}) of NecroForge is available. Update now?"):
                    logging.info("Update cancelled by user.")
                    return

                # Find the necroforge.exe asset
                asset = next((a for a in release['assets'] if a['name'] == 'necroforge.exe'), None)
                if not asset:
                    msg = "No executable found in the latest release."
                    logging.error(msg)
                    messagebox.showerror("Update Error", msg)
                    return

                # Download the new executable
                logging.info(f"Downloading new executable to {temp_exe}...")
                with open(temp_exe, 'wb') as f:
                    f.write(requests.get(asset['browser_download_url'], timeout=10).content)
                time.sleep(0.5)  # Ensure file is written
                if not os.path.exists(temp_exe):
                    msg = f"Update failed: Temporary file {temp_exe} was not created."
                    logging.error(msg)
                    messagebox.showerror("Update Error", msg)
                    return

                # Create update.bat for Windows
                if platform.system() == "Windows":
                    batch_content = f"""@echo off
echo Updating NecroForge...
ping 127.0.0.1 -n 10 >nul
move /Y "{temp_exe}" "{os.path.join(os.path.dirname(self.CURRENT_FILE), 'necroforge.exe')}" || (
    echo Failed to replace necroforge.exe
    exit /b 1
)
echo Replaced necroforge.exe
del "{temp_exe}" || (
    echo Could Not Find {temp_exe}
)
echo Deleted temporary file
start "" "{os.path.join(os.path.dirname(self.CURRENT_FILE), 'necroforge.exe')}"
echo Restarted application
del "{batch_path}"
exit
"""
                    logging.info(f"Writing batch file to {batch_path}...")
                    with open(batch_path, 'w', encoding='utf-8') as batch_file:
                        batch_file.write(batch_content)
                    time.sleep(0.5)  # Ensure file is written
                    if not os.path.exists(batch_path):
                        msg = f"Update failed: Batch file {batch_path} was not created."
                        logging.error(msg)
                        messagebox.showerror("Update Error", msg)
                        return
                    logging.info(f"Executing batch file: {batch_path}")
                    subprocess.Popen(['cmd', '/c', batch_path], shell=True)
                    self.root.destroy()
                else:
                    msg = "Updates are only supported on Windows."
                    logging.error(msg)
                    messagebox.showerror("Update Error", msg)
                    return
            else:
                logging.info("No update needed, versions match.")
                messagebox.showinfo("Update", "NecroForge is up to date.")
        except requests.RequestException as e:
            msg = f"Update failed: Network error while fetching update ({str(e)})."
            logging.error(msg)
            messagebox.showerror("Update Error", msg)
        except PermissionError as e:
            msg = f"Update failed: Insufficient permissions to write to {temp_exe} or {self.CURRENT_FILE} ({str(e)})."
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
    # Clean up stale files
    for path in ["update.bat", "update.sh", "necroforge_tmp.exe"]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logging.info(f"Cleaned up stale file: {path}")
            except Exception as e:
                logging.warning(f"Failed to clean up stale file {path}: {str(e)}")

    root = tk.Tk()
    app = NecroForgeApp(root)
    root.mainloop()