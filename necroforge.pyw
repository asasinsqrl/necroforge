# necroforge.pyw
# User-friendly version of NecroForge with simplified setup and guidance.

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
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
import threading
import queue
try:
    from charset_normalizer import detect
    import html.parser
    import jsonschema
except ImportError:
    detect = None
    html = None
    jsonschema = None  # Optional dependencies for validation

# Configure logging
logging.basicConfig(
    filename='necroforge_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    filemode='a'
)

class NecroForgeApp:
    """User-friendly GUI application for generating files with minimal setup."""
    VERSION = "1.2.0"  # User-friendly update
    UPDATE_URL = "https://api.github.com/repos/asasinsqrl/NecroForge/releases/latest"
    CURRENT_FILE = os.path.abspath(__file__)
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "necroforge_config.json")

    def __init__(self, root):
        self.root = root
        self.root.title("NecroForge - Easy File Creator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Welcome dialog for first-time users
        if not os.path.exists(self.CONFIG_FILE):
            messagebox.showinfo("Welcome to NecroForge", 
                "Hi! NecroForge helps you create files easily. \n\n"
                "1. Click 'Create Sample Input' to get started.\n"
                "2. Choose an output folder.\n"
                "3. Click 'Generate Files' to create your files!\n\n"
                "No coding needed—just follow the steps. Enjoy!")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(12, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready to create files!")
        tk.Label(self.main_frame, textvariable=self.progress_var, font=("Arial", 10, "italic")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        tk.Label(self.main_frame, text=f"NecroForge v{self.VERSION}", font=("Arial", 12, "bold"), fg="#4CAF50").grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        tk.Button(self.main_frame, text="Check for Updates", command=self.start_update_check, width=15, font=("Arial", 10)).grid(row=1, column=1, pady=5, sticky="e")

        # Simplified input section with tooltip
        tk.Label(self.main_frame, text="Pick Your Input File:", font=("Arial", 12)).grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        tk.Label(self.main_frame, text="Use the sample or your own .txt file (e.g., FILE: path, CONTENT:, ---)", font=("Arial", 10, "italic"), wraplength=500).grid(row=3, column=0, columnspan=2, sticky="w")
        self.file_path_var = tk.StringVar(value="sample_ultimate.txt")  # Default sample
        tk.Entry(self.main_frame, textvariable=self.file_path_var, width=50).grid(row=4, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_file, width=10).grid(row=4, column=1, pady=5, padx=5)
        tk.Button(self.main_frame, text="Create Sample Input", command=self.create_sample_input, width=15).grid(row=5, column=0, columnspan=2, pady=5)
        self.file_path_var.trace('w', lambda *args: self.save_config())  # Auto-save on change

        # Simplified output section with tooltip
        tk.Label(self.main_frame, text="Choose Where to Save:", font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10, sticky="w")
        self.output_dir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "MyFiles"))  # Default output
        tk.Entry(self.main_frame, textvariable=self.output_dir_var, width=50).grid(row=7, column=0, pady=5, padx=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_output_dir, width=10).grid(row=7, column=1, pady=5, padx=5)
        self.output_dir_var.trace('w', lambda *args: self.save_config())  # Auto-save on change

        # Minimal options with tooltips
        self.use_templates_var = tk.BooleanVar(value=True)  # Default on
        tk.Checkbutton(self.main_frame, text="Use ready-made templates", variable=self.use_templates_var, font=("Arial", 10)).grid(row=8, column=0, columnspan=2, pady=5, sticky="w")
        CreateToolTip(self.main_frame, "Adds basic HTML, CSS, and JS templates if files are empty.")
        self.validate_css_var = tk.BooleanVar(value=False)  # Default off to avoid warnings
        tk.Checkbutton(self.main_frame, text="Check CSS (may show warnings)", variable=self.validate_css_var, font=("Arial", 10)).grid(row=9, column=0, columnspan=2, pady=5, sticky="w")
        CreateToolTip(self.main_frame, "Turn this on to check CSS, but it might warn about errors.")
        self.overwrite_var = tk.BooleanVar(value=False)  # Default off
        tk.Checkbutton(self.main_frame, text="Replace existing files", variable=self.overwrite_var, font=("Arial", 10)).grid(row=10, column=0, columnspan=2, pady=5, sticky="w")
        CreateToolTip(self.main_frame, "Check this to overwrite files that already exist.")

        self.generate_button = tk.Button(
            self.main_frame, text="Create My Files Now!", command=self.start_generate_files,
            width=20, height=2, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white"
        )
        self.generate_button.grid(row=11, column=0, columnspan=2, pady=20)

        self.load_config()

    def load_config(self):
        """Load last used settings from config file with defaults."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.file_path_var.set(config.get('input_file', 'sample_ultimate.txt'))
                self.output_dir_var.set(config.get('output_dir', os.path.join(os.path.expanduser("~"), "Desktop", "MyFiles")))
                self.use_templates_var.set(config.get('use_templates', True))
                self.validate_css_var.set(config.get('validate_css', False))
                self.overwrite_var.set(config.get('overwrite', False))
        except Exception as e:
            logging.warning(f"Failed to load config: {str(e)}")

    def save_config(self):
        """Save current settings to config file."""
        config = {
            'input_file': self.file_path_var.get(),
            'output_dir': self.output_dir_var.get(),
            'folder_name': self.folder_name_var.get(),
            'use_templates': self.use_templates_var.get(),
            'validate_css': self.validate_css_var.get(),
            'overwrite': self.overwrite_var.get()
        }
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logging.warning(f"Failed to save config: {str(e)}")

    def browse_file(self):
        """Open file dialog to select input file with guidance."""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("JSON", "*.json"), ("YAML", "*.yaml")])
        if file_path:
            self.file_path_var.set(file_path)
            messagebox.showinfo("File Selected", "Great choice! Now pick where to save your files.")

    def browse_output_dir(self):
        """Open directory dialog to select output directory with guidance."""
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_var.set(output_dir)
            messagebox.showinfo("Folder Selected", "Awesome! You're ready to create files!")

    def sanitize_path(self, file_name, output_path):
        """Sanitize file path to prevent path traversal and invalid characters."""
        safe_name = re.sub(r'[<>:"|?*]', '', file_name)
        safe_name = safe_name.replace('..', '').replace('//', '/').strip('/')
        if not safe_name:
            raise ValueError("Sanitized file name is empty")
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
                    try:
                        with open(os.path.join(self.TEMPLATE_DIR, file_name), 'r', encoding='utf-8') as f:
                            templates[file_name] = f.read()
                    except Exception as e:
                        logging.warning(f"Failed to load template {file_name}: {str(e)}")
        return templates

    def parse_input_file(self, input_file):
        """Parse input file in block-based or JSON format with error recovery."""
        files = []
        if input_file.endswith('.json'):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for file_name, content in data.items():
                    files.append((file_name, content))
            except Exception as e:
                logging.error(f"Couldn’t read JSON file {input_file}: {str(e)}")
                messagebox.showwarning("JSON Issue", f"Problem with {input_file}. Using any valid parts.")
        else:  # Assume block-based .txt
            current_file = None
            current_content = []
            in_content = False
            invalid_lines = []
            try:
                if detect:
                    with open(input_file, 'rb') as f:
                        raw_data = f.read()
                        encoding = detect(raw_data).get('encoding', 'utf-8') or 'utf-8'
                else:
                    encoding = 'utf-8'
                with open(input_file, 'r', encoding=encoding, errors='replace') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    line = line.rstrip()
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    if line.startswith('FILE:'):
                        if current_file and in_content:
                            files.append((current_file, '\n'.join(current_content)))
                            current_content = []
                        current_file = line[5:].strip()
                        if not current_file:
                            invalid_lines.append(f"Line {i}: Empty FILE path")
                            current_file = None
                        in_content = False
                    elif line == 'CONTENT:':
                        if not current_file:
                            invalid_lines.append(f"Line {i}: CONTENT: found without FILE:")
                            continue
                        in_content = True
                    elif line == '---':
                        if current_file and in_content:
                            files.append((current_file, '\n'.join(current_content)))
                            current_file = None
                            current_content = []
                            in_content = False
                        else:
                            invalid_lines.append(f"Line {i}: Invalid ---")
                    elif in_content:
                        current_content.append(line)
                    else:
                        invalid_lines.append(f"Line {i}: Unexpected text")
                if current_file and in_content:
                    files.append((current_file, '\n'.join(current_content)))
                if invalid_lines:
                    logging.warning(f"Skipped issues in {input_file}: {invalid_lines}")
                    messagebox.showinfo("Notice", f"Some lines in {input_file} were skipped. Still created {len(files)} files!")
            except Exception as e:
                logging.error(f"Couldn’t open {input_file}: {str(e)}")
                messagebox.showwarning("File Error", f"Couldn’t read {input_file}. Try the sample input.")
        return files if files else [(f"output_{time.time()}.txt", "Default content")]  # Fallback

    def validate_content(self, file_path, content):
        """Validate content with minimal disruption."""
        if file_path.endswith('.css') and self.validate_css_var.get():
            if not self.validate_css(content):
                logging.warning(f"CSS issue in {file_path}: Generated anyway.")
                return False  # Proceed without warning popup to keep it simple
        return True  # Skip HTML/JSON validation by default for ease

    def validate_css(self, content):
        """Validate CSS content with silent handling."""
        in_comment = False
        in_string = None
        braces = 0
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            pos = 0
            while pos < len(line):
                char = line[pos]
                if in_comment:
                    if pos + 1 < len(line) and char == '*' and line[pos + 1] == '/':
                        in_comment = False
                        pos += 2
                        continue
                elif in_string:
                    if char == in_string and line[pos - 1] != '\\':
                        in_string = None
                    pos += 1
                    continue
                elif char == '/' and pos + 1 < len(line) and line[pos + 1] == '*':
                    in_comment = True
                    pos += 2
                    continue
                elif char in ('"', "'"):
                    in_string = char
                    pos += 1
                    continue
                elif char == '{':
                    braces += 1
                elif char == '}':
                    braces -= 1
                pos += 1
            if braces < 0:
                logging.warning(f"Unbalanced brace in CSS line {i}")
                return False
        if in_comment:
            logging.warning("Unclosed comment in CSS")
            return False
        if in_string:
            logging.warning("Unclosed string in CSS")
            return False
        if braces != 0:
            logging.warning(f"Unbalanced braces in CSS: {braces}")
            return False
        return True

    def generate_files(self):
        """Generate files with user-friendly feedback."""
        input_file = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        use_templates = self.use_templates_var.get()
        overwrite = self.overwrite_var.get()

        if not os.path.exists(input_file):
            messagebox.showwarning("Oops!", f"Couldn’t find {input_file}. Creating a sample for you!")
            self.create_sample_input()
            input_file = os.path.join(os.path.dirname(input_file), "sample_ultimate.txt")

        if not output_dir:
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "MyFiles")
            self.output_dir_var.set(output_dir)
            messagebox.showinfo("Default Set", "Using Desktop/MyFiles as your save spot!")

        output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0])

        self.root.after(0, lambda: self.progress_var.set(f"Making folder: {output_path}"))
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            logging.error(f"Folder issue with {output_path}: {str(e)}")
            messagebox.showerror("Error", f"Couldn’t make folder: {str(e)}. Try a different spot.")
            self.root.after(0, lambda: self.generate_button.config(state='normal'))
            return

        try:
            files = self.parse_input_file(input_file)
        except Exception as e:
            logging.error(f"Input problem with {input_file}: {str(e)}")
            messagebox.showerror("Error", f"Couldn’t read input: {str(e)}. Using a default file.")
            files = [(f"output_{time.time()}.txt", "Default content")]

        templates = self.load_templates()
        generated_files = []
        file_queue = queue.Queue()
        for file_name, content in files:
            file_queue.put((file_name, content))

        def process_file():
            while not file_queue.empty():
                file_name, content = file_queue.get()
                i = len(generated_files) + 1
                try:
                    file_path = self.sanitize_path(file_name, output_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    if os.path.exists(file_path) and not overwrite:
                        logging.warning(f"Skipped {file_path} - already exists")
                        continue
                    if not self.validate_content(file_path, content):
                        logging.warning(f"Issues with {file_name} - created anyway")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if use_templates and os.path.basename(file_path) in templates and not content.strip():
                            f.write(templates[os.path.basename(file_path)].format(title=os.path.basename(file_path), content=""))
                        else:
                            f.write(content)
                    generated_files.append(file_path)
                    logging.info(f"Created: {file_path}")
                    self.root.after(0, lambda: self.progress_var.set(f"Making file {i}/{len(files)}"))
                except Exception as e:
                    logging.error(f"Failed on {file_name}: {str(e)}")
                file_queue.task_done()

        threads = []
        for _ in range(min(4, len(files))):
            t = threading.Thread(target=process_file)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        if generated_files:
            self.root.after(0, lambda: messagebox.showinfo("Success!", f"Created {len(generated_files)} files in {output_path}!"))
            self.root.after(0, lambda: self.progress_var.set(f"Done! Made {len(generated_files)} files"))
        else:
            self.root.after(0, lambda: messagebox.showwarning("Notice", "No files made. Check your input or folder."))
            self.root.after(0, lambda: self.progress_var.set("No files made"))
        self.root.after(0, lambda: self.generate_button.config(state='normal'))
        self.save_config()

    def preview_input(self):
        """Show a preview of the input file contents with guidance."""
        input_file = self.file_path_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showwarning("Preview Issue", "Pick or create an input file first!")
            return
        try:
            files = self.parse_input_file(input_file)
            preview_text = "What You'll Create:\n\n"
            for i, (file_name, content) in enumerate(files):
                preview_text += f"File {i+1}: {file_name}\nContent:\n{content}\n{'-'*40}\n"
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Preview Your Files")
            preview_window.geometry("600x400")
            text_area = scrolledtext.ScrolledText(preview_window, height=20, width=80, wrap=tk.WORD)
            text_area.pack(padx=10, pady=10, fill='both', expand=True)
            text_area.insert(tk.END, preview_text)
            text_area.config(state='disabled')
            messagebox.showinfo("Preview Ready", "Take a look! Click OK to close.")
        except Exception as e:
            logging.error(f"Preview failed for {input_file}: {str(e)}")
            messagebox.showerror("Preview Error", f"Couldn’t preview: {str(e)}")

    def create_sample_input(self):
        """Create a sample input file with clear instructions."""
        output_dir = self.output_dir_var.get()
        if not output_dir:
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            self.output_dir_var.set(output_dir)
        sample_content = """# Easy Start for NecroForge
# Write FILE: then a path, CONTENT: then your text, end with ---
FILE: index.html
CONTENT:
<!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body><h1>Welcome!</h1></body>
</html>
---
FILE: assets/styles/style.css
CONTENT:
body { background-color: #f0f0f0; }
---
FILE: assets/scripts/script.js
CONTENT:
console.log("Hello!");
---
"""
        sample_path = os.path.join(output_dir, "sample_ultimate.txt")
        if os.path.exists(sample_path):
            if not messagebox.askyesno("File Exists", f"Replace {sample_path}?"):
                return
        try:
            with open(sample_path, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            messagebox.showinfo("Sample Ready!", f"Sample file saved at {sample_path}. Use it to start!")
            self.file_path_var.set(sample_path)
            self.save_config()
        except Exception as e:
            logging.error(f"Sample creation failed: {str(e)}")
            messagebox.showerror("Error", f"Couldn’t save sample: {str(e)}")

    def start_update_check(self):
        """Start update check in a separate thread with simple feedback."""
        self.generate_button.config(state='disabled')
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        """Check for and apply updates from GitHub with user guidance."""
        temp_file = os.path.join(os.path.dirname(self.CURRENT_FILE), "necroforge_tmp")
        self.root.after(0, lambda: self.progress_var.set("Checking for updates..."))
        logging.info(f"Update check started. URL: {self.UPDATE_URL}")
        try:
            for path in [temp_file, os.path.join(os.path.dirname(self.CURRENT_FILE), "update.bat")]:
                if os.path.exists(path):
                    os.remove(path)
                    logging.info(f"Cleaned up: {path}")
            response = requests.get(self.UPDATE_URL, timeout=5)
            response.raise_for_status()
            release = response.json()
            latest_version = release['tag_name'].lstrip('v').strip()
            if latest_version != self.VERSION:
                if self.root.after(0, lambda: messagebox.askyesno("Update Available", f"New version {latest_version} is here! Update now?")):
                    asset = next((a for a in release['assets'] if a['name'].endswith(('necroforge.exe', 'necroforge'))), None)
                    if not asset:
                        raise ValueError("No update file found")
                    with open(temp_file, 'wb') as f:
                        f.write(requests.get(asset['browser_download_url'], timeout=10).content)
                    new_file = os.path.join(os.path.dirname(self.CURRENT_FILE), 'necroforge' + ('.exe' if platform.system() == "Windows" else ''))
                    shutil.move(temp_file, new_file)
                    os.chmod(new_file, 0o755)
                    subprocess.Popen([new_file])
                    self.root.after(0, self.root.destroy)
                else:
                    self.root.after(0, lambda: self.progress_var.set("Update skipped."))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Up to Date", "You’ve got the latest NecroForge!"))
                self.root.after(0, lambda: self.progress_var.set("No updates needed."))
        except Exception as e:
            logging.error(f"Update failed: {str(e)}")
            self.root.after(0, lambda: messagebox.showwarning("Update Issue", f"Couldn’t check updates: {str(e)}. Try again later."))
        finally:
            self.root.after(0, lambda: self.generate_button.config(state='normal'))

    def start_generate_files(self):
        """Start file generation in a separate thread with encouraging feedback."""
        self.generate_button.config(state='disabled')
        threading.Thread(target=self.generate_files, daemon=True).start()

# Tooltip class for user guidance
class CreateToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 10))
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def main():
    """Main entry point for NecroForge with cleanup."""
    for path in ["necroforge_tmp", "necroforge_tmp.exe", "update.bat"]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logging.info(f"Cleaned up: {path}")
            except Exception as e:
                logging.warning(f"Cleanup failed for {path}: {str(e)}")
    root = tk.Tk()
    app = NecroForgeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()