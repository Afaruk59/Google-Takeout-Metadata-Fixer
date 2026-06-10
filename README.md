# Google Takeout Metadata Fixer

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A robust, zero-dependency Python toolkit designed to solve the common issues with media files downloaded from Google Takeout. When you export your Google Photos, the original creation and modification dates of your images and videos are often stripped from the file properties and placed into separate `.json` files. 

This toolkit intelligently parses those JSON files, extracts the original `photoTakenTime`, and restores the authentic creation and modification dates directly to the file system properties.

## 🚀 Key Features

*   **Zero Dependencies:** Uses only Python's standard library. No need to `pip install` external packages. It utilizes `ctypes` to interact directly with the Windows API to alter creation times.
*   **Smart JSON Matching:** Google Takeout is notorious for truncating JSON filenames (e.g., creating `.su.json` instead of `.supplemental-metadata.json`) or placing `(1)` suffix arbitrarily. This script uses intelligent prefix and regex matching to find the correct JSON file, even if it has been bizarrely renamed by Google.
*   **Filename Date Fallback:** If a JSON file is completely missing, the script features a fallback mechanism that extracts the date directly from standard camera filename patterns (e.g., `IMG_20240102_153714.jpg`, `VID_...`, WhatsApp formats).
*   **Duplicate Renamer:** Preparing to merge multiple folders into one? The included `rename_duplicates.py` recursively finds identically named files and sequentially numbers them (e.g., `IMG_123_1.jpg`) to prevent overwrite collisions.
*   **JSON Cleanup:** Once your dates are safely restored, use `delete_json_files.py` to recursively delete all leftover JSON files and declutter your archives.

## 🛠️ Included Scripts

### 1. `fix_google_takeout_dates.py` (The Main Restorer)
Scans the targeted directory and its subdirectories for media files (`.jpg`, `.mp4`, `.png`, etc.). It pairs each media file with its corresponding JSON file, extracts the UNIX epoch timestamp, and updates both the **Creation Time** and **Modification Time** on Windows.
```bash
# Usage
python fix_google_takeout_dates.py [path_to_directory]
```

### 2. `rename_duplicates.py` (Collision Preventer)
Scans recursively to find files with the exact same name across different folders. It renames the duplicates by appending a counter to the end of the file name. Perfect for preparing a mass merge of multiple yearly folders into a single root folder.
```bash
# Usage
python rename_duplicates.py [path_to_directory]
```

### 3. `delete_json_files.py` (The Cleaner)
Recursively finds and permanently deletes all `.json` files within the target directory tree. **Includes a safety prompt** to confirm before execution.
```bash
# Usage
python delete_json_files.py [path_to_directory]
```

### 4. `organize_by_year.py` (The Organizer)
Groups and moves all media files into specific folders categorized by their modification year (e.g., `2024`, `2023`). It smartly ignores script files and system directories. Perfect for organizing files after fixing their dates.
```bash
# Kullanım (Usage)
python organize_by_year.py [path_to_directory]
```

## 📋 Requirements
- **Python 3.8+**
- **Windows OS** (The script uses Windows-specific API `ctypes.windll.kernel32.SetFileTime` to alter the true "Creation Date" property. Running on macOS/Linux will still update the modification date via `os.utime`, but creation date requires OS-specific adaptations).

## 💡 How it Handles Google Takeout Quirks
1. **Truncated Names:** A file named `A_very_long_file_name.png` might get a JSON named `A_very_long_file_name.png.supplemental-metada.json`. The script uses `startswith()` matching to pair them successfully.
2. **Duplicate Numbering:** If Takeout creates `image(1).png`, it might create `image.png.supplemental-metadata(1).json`. The script automatically parses the `(N)` suffix and generates matching candidates.
3. **Missing JSONs:** Defaults to extracting timestamps using Regex patterns covering formats from Pixel, Samsung, WhatsApp, and generic Android/iOS devices.

## 📝 License
This project is licensed under the MIT License. Feel free to fork, modify, and distribute.
