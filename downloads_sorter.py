import os
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# -----------------------------
# File type mapping (by extension)
# -----------------------------
EXT_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heic", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".tsv", ".ods"},
    "Slides": {".ppt", ".pptx", ".key"},
    "Audio": {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Installers": {".exe", ".msi", ".msix"},
    "Code": {
        ".py", ".ipynb", ".java", ".c", ".cpp", ".h", ".hpp", ".js", ".ts",
        ".html", ".css", ".json", ".xml", ".yml", ".yaml", ".sql", ".sh", ".bat", ".ps1"
    },
}

CATEGORY_FOLDERS = set(EXT_MAP.keys()) | {"Other"}
LOGS_FOLDER_NAME = "_DownloadsSorterLogs"
SIGNATURE = "— Ali Nathani, 2026"

def category_for_file(path: Path) -> str:
    ext = path.suffix.lower()
    for cat, exts in EXT_MAP.items():
        if ext in exts:
            return cat
    return "Other"

def default_downloads_dir() -> Path:
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        return Path(userprofile) / "Downloads"
    return Path.home() / "Downloads"

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")

def safe_unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def write_log_line(log_path: Path, record: dict) -> None:
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def is_inside(path: Path, maybe_parent: Path) -> bool:
    try:
        path.resolve().relative_to(maybe_parent.resolve())
        return True
    except Exception:
        return False

def run_sort(downloads_dir: Path, dry_run: bool, assume_yes: bool) -> Path:
    logs_dir = downloads_dir / LOGS_FOLDER_NAME
    ensure_dir(logs_dir)
    log_path = logs_dir / f"move_log_{now_stamp()}.jsonl"

    for folder in CATEGORY_FOLDERS:
        ensure_dir(downloads_dir / folder)

    entries = list(downloads_dir.iterdir())

    planned = []
    category_dirs = {(downloads_dir / name).resolve() for name in CATEGORY_FOLDERS}
    logs_dir_resolved = logs_dir.resolve()

    for p in entries:
        if not p.is_file():
            continue
        if is_inside(p, logs_dir_resolved):
            continue
        if p.parent.resolve() in category_dirs:
            continue

        cat = category_for_file(p)
        dest = safe_unique_destination((downloads_dir / cat) / p.name)
        planned.append((p, dest, cat))

    if not planned:
        print("No top-level files found to organize.")
        return log_path

    print(f"Downloads folder: {downloads_dir}")
    print(f"Files to move (top-level only): {len(planned)}\n")

    for p, dest, cat in planned[:25]:
        print(f"[{cat}] {p.name}  ->  {dest}")
    if len(planned) > 25:
        print(f"... and {len(planned) - 25} more")

    if dry_run:
        print("\nDRY RUN: No files were moved.")
        print(f"Log would be: {log_path}")
        return log_path

    if not assume_yes:
        resp = input("\nProceed with moving these files? (y/n): ").strip().lower()
        if resp not in {"y", "yes"}:
            print("Cancelled. No files were moved.")
            return log_path

    moved_count = 0
    for src, dst, cat in planned:
        try:
            stat = src.stat()
            record = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "action": "move",
                "category": cat,
                "src": str(src),
                "dst": str(dst),
                "size_bytes": stat.st_size,
                "mtime_epoch": int(stat.st_mtime),
            }
            shutil.move(str(src), str(dst))
            write_log_line(log_path, record)
            moved_count += 1
        except Exception as e:
            write_log_line(log_path, {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "action": "error",
                "src": str(src),
                "dst": str(dst),
                "error": repr(e),
            })
            print(f"ERROR moving {src.name}: {e}")

    print(f"\nDone. Moved {moved_count} files.")
    print(f"Log saved to:\n{log_path}\n")
    print(SIGNATURE)

    return log_path

def run_undo(log_path: Path, dry_run: bool, assume_yes: bool) -> None:
    if not log_path.exists():
        print(f"Undo log not found: {log_path}")
        return

    moves = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("action") == "move":
                    moves.append(rec)
            except Exception:
                pass

    moves.reverse()

    print(f"Moves to undo: {len(moves)}")
    if dry_run:
        print("\nDRY RUN: No files were moved.")
        return

    if not assume_yes:
        resp = input("\nProceed with UNDO? (y/n): ").strip().lower()
        if resp not in {"y", "yes"}:
            print("Cancelled.")
            return

    for rec in moves:
        src = Path(rec["dst"])
        dst = Path(rec["src"])
        if src.exists():
            ensure_dir(dst.parent)
            shutil.move(str(src), str(safe_unique_destination(dst)))

    print("\nUndo complete.")
    print(SIGNATURE)

def main():
    parser = argparse.ArgumentParser(description="Organize Downloads by file type.")
    parser.add_argument("--downloads", type=str, default=str(default_downloads_dir()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--undo", type=str)

    args = parser.parse_args()
    downloads_dir = Path(args.downloads).expanduser()

    if not downloads_dir.exists():
        print("Invalid Downloads directory.")
        input("Press Enter to exit...")
        return

    if args.undo:
        run_undo(Path(args.undo), args.dry_run, args.yes)
    else:
        run_sort(downloads_dir, args.dry_run, args.yes)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()