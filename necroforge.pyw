#`necroforge.pyw` will parse this format, splitting files by `---` and reading `FILE` and `CONTENT` sections, eliminating the need for inline escaping #of quotes or newlines.

#---

### Updated `necroforge.pyw` (v1.0.12)
#This version uses the new block-based input format. It retains all prior features (no console, config persistence, etc.).

#python
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import requests
import shutil
import sys
import subprocess
import platform
import logging
import time
import re
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    filename='necroforge_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    filemode='a'
)

class NecroForgeApp:
    """GUI application for generating files from a .txt input and self-updating from GitHub."""
    VERSION = "1.0.12"  # Updated version
    UPDATE_URL = "https://api.github.com/repos/asasinsqrl/NecroForge/releases/latest"
    CURRENT_FILE = os.path.abspath(__file__)
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "necroforge_config.json")

    def __init__(self, root):
        """Initialize the NecroForge GUI."""
        self.root = root
        self.root.title("NecroForge")
        self.root.geometry("600x550")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.progress_var = tk.StringVar(value="Ready")
        tk.Label(self.main_frame, textvariable=self.progress_var, font=("Arial", 10, "italic")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        tk.Label(self.main_frame, text=f"NecroForge v{self.VERSION}", font=("Arial", 12, "bold"), fg="#4CAF50").grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        tk.Button(self.main_frame, text="Check for Updates", command=self.check_for_updates, width=15, font=("Arial", 10)).grid(row=1, column=1, pady=5, sticky="e")

        tk.Label(self.main_frame, text="Select Input .txt File:", font=("Arial", 12)).grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        tk.Label(self.main_frame, text="Format: FILE: <path>\nCONTENT:\n<lines>\n---", font=("Arial", 10, "italic")).grid(row=3, column=0, columnspan=2, sticky="w")
        self.file_path_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.file_path_var, width=50).grid(row=4, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_file, width=10).grid(row=4, column=1, pady=5, padx=5)
        tk.Button(self.main_frame, text="Preview Input", command=self.preview_input, width=15).grid(row=5, column=0, pady=5, sticky="w")
        tk.Button(self.main_frame, text="Create Sample Input", command=self.create_sample_input, width=15).grid(row=5, column=1, pady=5, sticky="e")

        tk.Label(self.main_frame, text="Output Directory:", font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10, sticky="w")
        self.output_dir_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.output_dir_var, width=50).grid(row=7, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_output_dir, width=10).grid(row=7, column=1, pady=5, padx=5)

        tk.Label(self.main_frame, text="Output Folder Name (optional):", font=("Arial", 12)).grid(row=8, column=0, columnspan=2, pady=10, sticky="w")
        self.folder_name_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.folder_name_var, width=50).grid(row=9, column=0, pady=5, padx=5)
        tk.Label(self.main_frame, text="Leave blank to use input file name", font=("Arial", 10, "italic")).grid(row=10, column=0, columnspan=2, pady=2, sticky="w")

        self.use_templates_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.main_frame,
            text="Use default templates for index.html, style.css, script.js",
            variable=self.use_templates_var,
            font=("Arial", 10)
        ).grid(row=11, column=0, columnspan=2, pady=5, sticky="w")

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
        self.generate_button.grid(row=12, column=0, columnspan=2, pady=20)

        self.load_config()

    def load_config(self):
        """Load last used input file and output directory from config file."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                input_file = config.get('input_file', '')
                output_dir = config.get('output_dir', '')
                if input_file and os.path.exists(input_file):
                    self.file_path_var.set(input_file)
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    self.folder_name_var.set(base_name)
                if output_dir and os.path.exists(output_dir):
                    self.output_dir_var.set(output_dir)
                logging.info(f"Loaded config: input_file={input_file}, output_dir={output_dir}")
        except Exception as e:
            logging.warning(f"Failed to load config: {str(e)}")

    def save_config(self, input_file=None, output_dir=None):
        """Save input file and output directory to config file."""
        try:
            config = {
                'input_file': input_file or self.file_path_var.get(),
                'output_dir': output_dir or self.output_dir_var.get()
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logging.info(f"Saved config: {config}")
        except Exception as e:
            logging.warning(f"Failed to save config: {str(e)}")

    def browse_file(self):
        """Open file dialog to select input .txt file."""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path_var.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.folder_name_var.set(base_name)
            self.save_config(input_file=file_path)
            logging.info(f"Selected input file: {file_path}")

    def browse_output_dir(self):
        """Open directory dialog to select output directory."""
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_var.set(output_dir)
            self.save_config(output_dir=output_dir)
            logging.info(f"Selected output directory: {output_dir}")

    def check_write_permissions(self, path):
        """Check if the directory has write permissions."""
        directory = os.path.dirname(path)
        return os.access(directory, os.W_OK)

    def sanitize_path(self, file_name, output_path):
        """Sanitize file path to prevent path traversal and invalid characters."""
        safe_name = re.sub(r'[^\w\.\-/]', '', file_name)
        safe_name = safe_name.replace('..', '').replace('//', '/').strip('/')
        full_path = os.path.join(output_path, safe_name)
        if not Path(full_path).resolve().is_relative_to(Path(output_path).resolve()):
            raise ValueError(f"Invalid file path: {file_name} attempts path traversal")
        return full_path

    def load_templates(self):
        """Load templates from TEMPLATE_DIR or use defaults."""
        templates = {
            'index.html': '<html><head><title>{title}</title></head><body>{content}</body></html>',
            'style.css': 'body { font-family: Arial, sans-serif; }',
            'script.js': 'console.log("Generated by Necromancer");'
        }
        if os.path.exists(self.TEMPLATE_DIR):
            for file_name in os.listdir(self.TEMPLATE_DIR):
                if file_name.endswith(('.html', '.css', '.js')):
                    with open(os.path.join(self.TEMPLATE_DIR, file_name), 'r', encoding='utf-8') as f:
                        templates[file_name] = f.read()
        return templates

    def parse_input_file(self, input_file):
        """Parse the input .txt file with block-based format (FILE, CONTENT, ---)."""
        files = []
        current_file = None
        current_content = []
        in_content = False

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(input_file, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            except Exception as e:
                raise ValueError(f"Failed to read input file: {str(e)}")

        for i, line in enumerate(lines):
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('FILE:'):
                if current_file and in_content:
                    files.append((current_file, '\n'.join(current_content)))
                    current_content = []
                current_file = line[5:].strip()
                in_content = False
            elif line == 'CONTENT:':
                if not current_file:
                    raise ValueError(f"Line {i+1}: CONTENT: found without preceding FILE:")
                in_content = True
            elif line == '---':
                if current_file and in_content:
                    files.append((current_file, '\n'.join(current_content)))
                    current_file = None
                    current_content = []
                    in_content = False
            elif in_content:
                current_content.append(line)
            else:
                raise ValueError(f"Line {i+1}: Invalid format, expected FILE:, CONTENT:, or ---")

        if current_file and in_content:
            files.append((current_file, '\n'.join(current_content)))

        if not files:
            raise ValueError("No valid files found in input")

        return files

    def preview_input(self):
        """Show a preview of the input .txt file contents."""
        input_file = self.file_path_var.get()
        if not input_file:
            messagebox.showwarning("Warning", "Select an input file to preview")
            return

        try:
            files = self.parse_input_file(input_file)
            preview_text = "Input File Preview:\n\n"
            for i, (file_name, content) in enumerate(files):
                preview_text += f"File {i+1}: {file_name}\nContent:\n{content}\n{'-'*40}\n"
            if not files:
                preview_text += "No valid files found"
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Input File Preview")
            preview_window.geometry("600x400")
            text_area = scrolledtext.ScrolledText(preview_window, height=20, width=80, wrap=tk.WORD)
            text_area.pack(padx=10, pady=10)
            text_area.insert(tk.END, preview_text)
            text_area.config(state='disabled')
        except Exception as e:
            logging.error(f"Failed to preview input file {input_file}: {str(e)}")
            messagebox.showerror("Error", f"Failed to preview input file: {str(e)}")

    def create_sample_input(self):
        """Create a sample input .txt file with block-based format."""
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("Warning", "Select an output directory to save sample file")
            return

        sample_content = """# Sample input file for NecroForge
# Format: FILE: <path>
# CONTENT:
# <lines>
# ---
FILE: index.html
CONTENT:
<!DOCTYPE html>
<html>
<head>
    <title>Sample</title>
</head>
<body>
    <h1>Hello!</h1>
</body>
</html>
---
FILE: css/style.css
CONTENT:
body {
    background-color: #f0f0f0;
    font-family: Arial, sans-serif;
}
.container {
    padding: 10px;
}
---
FILE: js/script.js
CONTENT:
console.log("Sample script");
function init() {
    alert("Loaded");
}
---
"""
        sample_path = os.path.join(output_dir, "sample_input.txt")
        try:
            with open(sample_path, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            messagebox.showinfo("Success", f"Sample input file created at {sample_path}")
            self.file_path_var.set(sample_path)
            self.save_config(input_file=sample_path)
            logging.info(f"Created sample input file: {sample_path}")
        except Exception as e:
            logging.error(f"Failed to create sample input file: {str(e)}")
            messagebox.showerror("Error", f"Failed to create sample input file: {str(e)}")

    def check_for_updates(self):
        """Check for and apply updates from GitHub (Windows only)."""
        temp_exe = os.path.join(os.path.dirname(self.CURRENT_FILE), "necroforge_tmp.exe")
        batch_path = os.path.join(os.path.dirname(self.CURRENT_FILE), "update.bat")
        self.progress_var.set("Checking for updates...")
        self.root.update()

        logging.info(f"Starting update check. URL: {self.UPDATE_URL}")
        try:
            for path in [temp_exe, batch_path]:
                if os.path.exists(path):
                    os.remove(path)
                    logging.info(f"Cleaned up: {path}")

            if not self.check_write_permissions(self.CURRENT_FILE):
                raise PermissionError(f"No write permission for {os.path.dirname(self.CURRENT_FILE)}")

            response = requests.get(self.UPDATE_URL, timeout=5)
            response.raise_for_status()
            release = response.json()
            latest_version = release['tag_name'].lstrip('v')
            logging.info(f"Latest version: {latest_version}, Current version: {self.VERSION}")

            if latest_version != self.VERSION:
                if not messagebox.askyesno("Update Available", f"Version {latest_version} available. Update now?"):
                    logging.info("Update cancelled by user")
                    self.progress_var.set("Update cancelled")
                    return

                asset = next((a for a in release['assets'] if a['name'] == 'necroforge.exe'), None)
                if not asset:
                    raise ValueError("No executable found in the latest release")

                logging.info(f"Downloading update to {temp_exe}")
                with open(temp_exe, 'wb') as f:
                    f.write(requests.get(asset['browser_download_url'], timeout=10).content)
                time.sleep(0.5)
                if not os.path.exists(temp_exe):
                    raise FileNotFoundError(f"Temporary file {temp_exe} not created")

                if platform.system() == "Windows":
                    batch_content = f"""@echo off
echo Updating NecroForge...
ping 127.0.0.1 -n 10 >nul
move /Y "{temp_exe}" "{os.path.join(os.path.dirname(self.CURRENT_FILE), 'necroforge.exe')}" || (
    echo Failed to replace necroforge.exe
    exit /b 1
)
del "{temp_exe}"
start "" "{os.path.join(os.path.dirname(self.CURRENT_FILE), 'necroforge.exe')}"
del "{batch_path}"
exit
"""
                    with open(batch_path, 'w', encoding='utf-8') as batch_file:
                        batch_file.write(batch_content)
                    time.sleep(0.5)
                    subprocess.Popen(['cmd', '/c', batch_path], shell=True)
                    self.root.destroy()
                else:
                    raise NotImplementedError("Updates supported only on Windows")
            else:
                messagebox.showinfo("Update", "NecroForge is up to date")
                self.progress_var.set("No updates needed")
        except Exception as e:
            logging.error(f"Update failed: {str(e)}", exc_info=True)
            messagebox.showerror("Update Error", f"Update failed: {str(e)}")
            self.progress_var.set("Update failed")

    def generate_files(self):
        """Generate files from input .txt file in the specified output directory."""
        input_file = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        folder_name = self.folder_name_var.get()
        use_templates = self.use_templates_var.get()

        if not input_file or not output_dir:
            messagebox.showerror("Error", "Select both an input file and output directory")
            self.progress_var.set("Missing input or output")
            return

        if not folder_name:
            folder_name = os.path.splitext(os.path.basename(input_file))[0]
        output_path = os.path.join(output_dir, folder_name)

        self.progress_var.set(f"Creating output directory: {output_path}")
        self.root.update()
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create output directory {output_path}: {str(e)}")
            messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
            self.progress_var.set("Directory creation failed")
            return

        try:
            files = self.parse_input_file(input_file)
        except Exception as e:
            logging.error(f"Failed to parse input file {input_file}: {str(e)}")
            messagebox.showerror("Error", f"Failed to parse input file: {str(e)}")
            self.progress_var.set("Input file parse error")
            return

        templates = self.load_templates()
        generated_files = []
        for i, (file_name, content) in enumerate(files):
            self.progress_var.set(f"Processing file {i+1}/{len(files)}")
            self.root.update()
            try:
                if not file_name:
                    raise ValueError(f"Empty file name at file {i+1}")

                file_path = self.sanitize_path(file_name, output_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    if use_templates and os.path.basename(file_path) in templates and not content.strip():
                        f.write(templates[os.path.basename(file_path)].format(title=os.path.basename(file_path), content=""))
                    else:
                        if file_path.endswith('.css'):
                            if '{' not in content or '}' not in content:
                                raise ValueError("Invalid CSS syntax: missing braces")
                        f.write(content)
                generated_files.append(file_path)
                logging.info(f"Generated file: {file_path}")
            except Exception as e:
                logging.error(f"Failed to process file {i+1}: {file_name}, Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to write {file_name}: {str(e)}")
                self.progress_var.set(f"Failed to process file {i+1}")
                return

        if generated_files:
            messagebox.showinfo("Success", f"Generated {len(generated_files)} files in {output_path}")
            self.progress_var.set(f"Generated {len(generated_files)} files")
        else:
            messagebox.showwarning("Warning", "No files generated")
            self.progress_var.set("No files generated")

def main():
    """Main entry point for NecroForge."""
    for path in ["necroforge_tmp.exe", "update.bat"]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logging.info(f"Cleaned up stale file: {path}")
            except Exception as e:
                logging.warning(f"Failed to clean up {path}: {str(e)}")

    root = tk.Tk()
    app = NecroForgeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()