THIS IS A TOOL CREATED BY AN AI FOR AIs. I instructed an AI to make this in order to streamline projects and avoid a lot of copypasta. It has worked well for me so far, but it needs to be tested to its limits. All you have to do is direct an AI that can create code to the GitHub repository and they should be able to work out what to do from there. But please know this is so far untested, so you might have to explain to them what the tool does in order for them to understand. They will have to make a .txt file in a certain way, detailed below. I made this in Windows, so no promises it will work elsewhere. Is NecroForge unique? No idea. Is it useful? That's for you to decide. It's free, so have fun. :)



Overview: NecroForge (v1.0.12) is a Python-based GUI application that automates the creation of multiple files, particularly for web development projects, from a single structured .txt input file. It uses a block-based format (FILE:, CONTENT:, ---) to generate files in a specified directory without requiring inline escaping of quotes or newlines. It includes a user-friendly interface, supports default or custom templates for web files (index.html, style.css, script.js), and offers a self-update feature (Windows only) to fetch the latest release from GitHub.Platform: Windows (self-update is Windows-only)
Dependencies: Python 3.x, tkinter (included with Python), requests (install via pip install requests)

Purpose: NecroForge streamlines file creation and project setup, ideal for:Web Development: Rapidly scaffolding projects with HTML, CSS, and JavaScript files.
Prototyping: Generating file structures for testing or demos.
Automation: Eliminating manual file creation for repetitive tasks.
Learning/Testing: Providing a sample input file to explore the format.

It’s designed for developers or users who want an efficient, visual tool to create project file structures.FeaturesFile Generation:Parses a .txt file with blocks defining file paths (FILE:) and content (CONTENT:), separated by ---.
Creates files in a user-specified output directory, supporting nested paths (e.g., css/style.css).

GUI Interface (via tkinter):Select input .txt file and output directory via file dialogs.
Preview input file contents.
Generate a sample input file for reference.
Specify a custom output folder name (defaults to input file name without .txt).
Option to use templates for empty index.html, style.css, or script.js files.
Displays progress and errors.

Self-Update (Windows Only):Checks GitHub (https://api.github.com/repos/asasinsqrl/NecroForge/releases/latest) for updates.
Downloads and replaces necroforge.exe if a newer version is available, then restarts.

Configuration:Saves input file and output directory in necroforge_config.json.

Logging:Logs actions and errors to necroforge_update.log.

Security:Sanitizes file paths to prevent path traversal.
Validates input format and CSS syntax (requires {}).

InstallationEnsure Python 3.x is installed with tkinter.
Install requests:bash

pip install requests

Download necroforge.pyw or necroforge.exe from GitHub.
(Optional) Add custom templates (index.html, style.css, script.js) to a templates directory in the same folder as the script/executable.

UsageLaunch:Run: python necroforge.pyw or double-click necroforge.exe (Windows).
The GUI displays the version and options.

Select Input File:Click "Browse" to choose a .txt file in the block-based format.
Use "Preview Input" to check contents or "Create Sample Input" to generate a sample file.

Select Output Directory:Click "Browse" to set the output directory.
Optionally set a custom "Output Folder Name" (defaults to input file name).

Configure Templates:Check "Use default templates" for empty web files.
Custom templates can be placed in the templates directory.

Generate Files:Click "Generate Files" to create files in the output directory.
Progress and results appear in the GUI.

Check Updates:Click "Check for Updates" to apply the latest version (Windows only).

Input File FormatThe .txt file uses this structure:

# Optional comment
FILE: <relative/path/to/file>
CONTENT:
<content lines>
---

FILE: Relative path (e.g., index.html, css/style.css).
CONTENT: File content, preserved as-is.
---: Separates file blocks.

Short Example Input File

FILE: index.html
CONTENT:
<!DOCTYPE html>
<html>
<body>
    <h1>Welcome</h1>
</body>
</html>
---
FILE: css/style.css
CONTENT:
body {
    color: blue;
}
---

Sample Input FileUse "Create Sample Input" to generate a more detailed example, such as:

# Sample input file for NecroForge
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
---
FILE: js/script.js
CONTENT:
console.log("Sample script");
---

TemplatesIf "Use default templates" is enabled, empty files use default or custom templates from the templates directory.
Default Templates:index.html: Basic HTML with {title} and {content} placeholders.
style.css: Arial font styling.
script.js: Console log.

Custom templates can override defaults in the templates folder.

LimitationsSelf-update is Windows-only (uses .exe and batch scripts).
Input files must be UTF-8 or Latin-1 encoded.
CSS files require valid {} syntax.
BigBrain mode is not supported.





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



If this tool is useless to you, I'm sorry. If it's not, you're welcome.  :)

