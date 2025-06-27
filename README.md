Smart File Organizer
A Python object-oriented application to automatically organize files in a folder by sorting them into subfolders based on their extensions.

🚀 Features
Automatic Organization: Sorts files by extension into categorized folders

Graphical Interface: Simple user interface built with tkinter

Preview Function: View which files will be moved before organizing

Undo Function: Roll back and restore files to their original location

Comprehensive Logging: Records all operations in log files

Error Handling: Robust handling of errors and filename conflicts

CLI Mode: Command-line usage for automation

🗂️ Supported File Categories
Images: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .svg, .webp, .ico

Documents: .pdf, .doc, .docx, .txt, .rtf, .odt, .pages

Spreadsheets: .xls, .xlsx, .csv, .ods

Presentations: .ppt, .pptx, .odp, .key

Videos: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v

Audio: .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a

Archives: .zip, .rar, .7z, .tar, .gz, .bz2

Code: .py, .js, .html, .css, .java, .cpp, .c, .php, .rb, .go

Executables: .exe, .msi, .dmg, .pkg, .deb, .rpm

Miscellaneous: All other file types

📁 Project Structure
bash
Copier
Modifier
smart-file-organizer/
├── main.py              # Main entry point
├── file_organizer.py    # File organization logic
├── gui.py               # tkinter GUI interface
├── logger.py            # Logging system
├── undo_manager.py      # Undo operation management
├── requirements.txt     # Python standard library dependencies
├── README.md            # This file
└── logs/                # Automatically created folder for logs
    ├── file_operations.log
    ├── moved_files.csv
    └── undo_data.json
🔧 Installation & Usage
Requirements
Python 3.6 or higher

tkinter (included with most Python installations)

Installation
Clone or download the project:

bash
Copier
Modifier
git clone <repo-url>
cd smart-file-organizer
No additional dependencies are required (uses only Python's standard library).

Usage
GUI Mode (recommended)
bash
Copier
Modifier
python main.py
Command-Line Mode
bash
Copier
Modifier
# Organize a specific folder
python main.py --cli "C:\Users\Username\Downloads"

# Organize the current directory
python main.py --cli .

# Show help
python main.py --help
🎯 GUI User Guide
1. Launch
Start the app with python main.py

The GUI will open

2. Folder Selection
Click "Browse" to choose the folder to organize

The path will appear in the text field

3. Preview
Click "Preview" to see which files will be moved

A popup window shows file distribution by category

4. Organization
Click "Start Organization" to begin

Confirm the operation in the dialog box

Track progress in the progress bar

5. Undo (if needed)
Click "Undo Last Operation" to revert

Files will return to their original location

6. View Logs
Logs are shown in the log area

Detailed logs are saved in the logs/ folder

🏗️ Object-Oriented Architecture
Main Classes
FileOrganizer
Responsibility: Core logic of file organization

Key Methods:

scan_directory() – Scans for files

organize_files() – Organizes and moves files

get_file_category() – Determines file category

Logger
Responsibility: Logs all operations

Features:

Text and CSV logging

Backup data for undo

Error logging

UndoManager
Responsibility: Manages undo operations

Features:

Records operations

Restores moved files

Handles filename conflicts

SmartFileOrganizerGUI
Responsibility: User interface

Features:

Folder selection

Preview and progress bars

Log display

📝 Usage Examples
Basic GUI Use
python
Copier
Modifier
from gui import SmartFileOrganizerGUI

app = SmartFileOrganizerGUI()
app.run()
Programmatic Use
python
Copier
Modifier
from file_organizer import FileOrganizer

# Create an instance
organizer = FileOrganizer()

# Set target directory
organizer.set_target_directory("/path/to/directory")

# Preview
preview = organizer.get_preview()
print(preview)

# Organize
success, message, results = organizer.organize_files()
if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")

# Undo if needed
if organizer.can_undo():
    undo_success, undo_message = organizer.undo_last_organization()
Adding Custom Categories
python
Copier
Modifier
organizer = FileOrganizer()

# Add custom category
organizer.add_custom_category("3D Models", [".obj", ".fbx", ".blend"])
organizer.add_custom_category("Fonts", [".ttf", ".otf", ".woff"])
📊 Log Formats
Text File (file_operations.log)
yaml
Copier
Modifier
[2025-06-27 14:30:15] MOVE: C:\Downloads\photo.jpg -> C:\Downloads\Images\photo.jpg (success)
[2025-06-27 14:30:16] MOVE: C:\Downloads\document.pdf -> C:\Downloads\Documents\document.pdf (success)
CSV File (moved_files.csv)
csv
Copier
Modifier
Timestamp,Source,Destination,Operation,Status
2025-06-27 14:30:15,C:\Downloads\photo.jpg,C:\Downloads\Images\photo.jpg,move,success
2025-06-27 14:30:16,C:\Downloads\document.pdf,C:\Downloads\Documents\document.pdf,move,success
⚠️ Error Handling
The app handles various error cases:

Duplicate Files: Automatically adds numeric suffixes

Insufficient Permissions: Displays detailed error messages

Missing Folders: Automatically creates necessary folders

File in Use: Handles file access/move errors gracefully

🔒 Safety
Automatic Backup: All operations are logged

Undo Function: Files can be restored

Path Validation: Checks if folder paths exist

Conflict Resolution: Prevents overwriting existing files

🧪 Testing
To test the app:

Create a test folder with various file types

Launch the app and select the folder

Use the “Preview” function to verify categorization

Organize the files

Test the “Undo” function

🤝 Contributing
To contribute:

Fork the repository

Create a new branch for your feature

Add your changes

Test your code

Submit a pull request

📄 License
This project is licensed under the MIT License. See the LICENSE file for more information.

🆘 Support
If you encounter issues:

Check the logs in the logs/ folder

Review error messages in the UI

Ensure you have the necessary folder permissions

🔄 Versions
Version 1.0.0
Full GUI support

Extension-based organization

Undo function

Comprehensive logging

CLI mode

Robust error handling
