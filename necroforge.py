import tkinter as tk
from tkinter import filedialog, messagebox
import os
import requests
import hashlib
import shutil
import sys
import subprocess

class NecroForgeApp:
    VERSION = "1.0.1"  # Updated version

    UPDATE_URL = "https://github.com/wowte/NecroForge/raw/main/necroforge.py"  # Replace with your URL
    TEMPLATE_URL = "https://github.com/wowte/NecroForge/raw/main/templates.json"  # Optional

    def __init__(self, root):
        self.root = root
        self.root.title("NecroForge")
        self.root.geometry("550x420")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Add version label at the top
        tk.Label(self.main_frame, text=f"NecroForge v{self.VERSION}", font=("Arial", 12, "bold"), fg="#4CAF50").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

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

        self.check_for_updates()

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

    def check_for_updates(self):
        try:
            response = requests.get(self.UPDATE_URL, timeout=5)
            if response.status_code == 200:
                latest_content = response.text
                local_hash = hashlib.md5(open(__file__, 'rb').read()).hexdigest()
                latest_hash = hashlib.md5(latest_content.encode()).hexdigest()
                if local_hash != latest_hash:
                    if messagebox.askyesno("Update Available", "A new version of NecroForge is available. Update now?"):
                        temp_path = sys.executable + ".tmp"
                        with open(temp_path, 'w', encoding='utf-8') as f:
                            f.write(latest_content)
                        subprocess.Popen([sys.executable, temp_path, "--update"])
                        self.root.quit()
        except Exception as e:
            print(f"Update check failed: {str(e)}")

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
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        shutil.move(sys.argv[0], sys.executable)
        print("NecroForge updated. Please restart the application.")
    else:
        root = tk.Tk()
        app = NecroForgeApp(root)
        root.mainloop()