THIS IS A TOOL CREATED BY AN AI FOR AIs. I instructed an AI to make this in order to streamline projects and avoid a lot of copypasta. It has worked well for me so far, but it needs to be tested to its limits. All you have to do is direct an AI that can create code to the GitHub repository and they should be able to work out what to do from there. But please know this is so far untested, so you might have to explain to them what the tool does in order for them to understand. They will have to make a .txt file in a certain way, detailed below. I made this in Windows, so no promises it will work elsewhere. Is NecroForge unique? No idea. Is it useful? That's for you to decide. It's free, so have fun. :)

Here is an example of how the .txt file should look (ignore the red bars if you're viewing this in Notepad or similar.):


# Example input.txt for NecroForge
# Each line is: file_path,content
# Use \n for newlines, keep content on one line per file

index.html,<!DOCTYPE html><html><head><title>NecroForge Sample</title><link rel="stylesheet" href="css/style.css"></head><body><h1>Welcome!</h1></body></html>
css/style.css,body { background-color: #1e1e1e; color: #fff; font-family: Arial, sans-serif; }\n.grid-container { display: grid; grid-template-columns: 1fr; }
js/script.js,console.log("Sample script loaded");\nfunction greet() { alert("Hello!"); }
config.json,{"app": "NecroForge", "version": "1.0.0"}
data.csv,name,age,city\nJohn,25,Seattle\nJane,30,Chicago
notes.txt,This is a sample note.\nCreated with NecroForge!

Note that the text script is in a single line with no spaces.

NecroForge - File Generation Tool
================================

Welcome to NecroForge, a tool to generate text-based files from a.txt file!

Requirements:
- Python 3.5+ installed on your system.
- Run 'py -m pip install requests` to enable automatic updates (no quotes).

How to Use:
1. Place your.txt file in a folder of your choosing or browse to it using the GUI.
2. Run necroforge.py (e.g., `py .\necroforge.py`).
3. Select your input.txt, output directory, and folder name, then click "Generate Files".
4. Uncheck "Use default templates" for custom content (e.g., web projects).

Update Process:
- Run updater.py (e.g., `py .\updater.py`) to check for updates.
- Or start necroforge.py; it will prompt you if an update is available.
- Replace the UPDATE_URL in both scripts with your update source (e.g., GitHub raw URL).



Contact:
- Report issues or suggest features to [your contact info].



What NecroForge Can Do: NecroForge reads a .txt file where each line specifies a file name and its content, separated by a comma. The current script writes this content directly to the specified file, using UTF-8 encoding. This means it can handle any file type whose content can be expressed as text, including:Markup Languages:HTML (e.g., web pages like your Necromancer Web Browser).
XML (e.g., configuration files, data structures).
Markdown (e.g., readme.md for documentation).

Style Sheets:CSS (e.g., style.css with background-color and layouts).
SCSS/Sass (text-based CSS preprocessors, if formatted as plain text).

Scripting Languages:JavaScript (e.g., script.js for your URL bar logic).
Python (e.g., simple scripts or configuration files).
Bash/Shell (e.g., .sh files for Unix commands).
PHP (e.g., web server scripts).

Data Formats:JSON (e.g., config.json for settings).
YAML (e.g., configuration files, if written as text).
CSV (e.g., data tables, though commas need careful handling with split(',', 1)).

Text Files:Plain Text (e.g., .txt for notes or logs).
Configuration Files (e.g., .ini, .cfg with key-value pairs).

Other Text-Based Formats:SQL (e.g., .sql files for database queries).
LaTeX (e.g., .tex for documents, if formatted as text).
INI (e.g., Windows-style config files).

Limitations: While NecroForge can generate files with text content, there are some limitations to consider:Binary Files: Files like images (.png, .jpg), executables (.exe), or compressed archives (.zip) cannot be created directly because their content is binary, not text. The script would write the text representation (e.g., “Placeholder for logo image”) as plain text, which won’t be a valid binary file. Workarounds include generating placeholder text files or using external tools to convert text to binary later.
Complex Formatting: Multi-line content in a .txt must be on a single line or use \n escapes. This can make large files cumbersome to write.
File Size: The .txt approach works best for small to medium-sized files. Very large content might be impractical to manage in a single line.
Execution: NecroForge generates files but doesn’t execute or compile them (e.g., it won’t run a .py script or render a .tex file into a PDF).

NOTE: The AI may be able to work around the image limitation by linking to an image file saved somewhere on the interwebs.Needs to be tested.



If this tool is useless to  you, I'm sorry. If it's not, you're welcome.  :)

