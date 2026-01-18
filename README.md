# Downloads Folder Cleaner (One-Click)

A small, safe utility that organizes files in your **Downloads** folder by file type.

If your Downloads folder is full of PDFs, images, installers, audio files, and random clutter — this tool cleans it up in one run.

---

## How to run (start here)

1. Download the executable for your system:
   - **Windows** → open the `windows-exe-file` folder and download the `.exe`
   - **macOS** → open the `macos-exe-file` folder and download the macOS executable

2. Save the file **anywhere** (Desktop, Downloads, or any folder — it does not matter).

3. Double-click the file to run it.
   - A small window will open.
   - The tool will show a preview of what it is about to do.
   - You will be asked **once** to confirm.

4. Confirm, and the tool will organize your Downloads folder.

No Python, setup, or configuration required.

---

## What this tool does

When you run it, the tool:

- Scans **only the top-level files** in your Downloads folder
- Creates folders (if they do not already exist), such as:
  - Documents
  - Images
  - Audio
  - Video
  - Spreadsheets
  - Slides
  - Archives
  - Installers
  - Code
  - Other
- Moves each file into the appropriate folder based on file type
- Shows a preview and asks **once** before making changes
- Logs every file move so the operation can be undone later

---

## What it does NOT do (by design)

- ❌ Does not look inside existing folders
- ❌ Does not guess what class, project, or topic a file belongs to
- ❌ Does not overwrite files
- ❌ Does not delete anything

This tool is intentionally conservative and safe.

---

## Undo / Recovery

Every run creates a log file inside: Downloads/_DownloadsSorterLogs/

This log records:
- Original file location
- New file location
- Timestamp

If needed, the same tool can use this log to **undo the changes** and restore files to their original locations.

---

## Edge cases handled safely

- If a folder (e.g., `Documents`, `Images`) already exists → it is reused
- If a file with the same name already exists → the file is renamed (e.g., `file (1).pdf`)
- If a file is locked or cannot be moved → it is skipped and logged
- If files were manually changed after sorting → undo skips them and reports it
- If no files are found → nothing happens

---

## Notes

- You may see a security warning the first time you run it (unsigned executable). This is normal for personal utilities.
  - Windows: click **More info → Run anyway**
  - macOS: right-click → **Open**
- Always review the preview before confirming.

---

— Ali Nathani, 2026
