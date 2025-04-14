import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
try:
  import exifread
except ModuleNotFoundError:
  print("exifread isn't intalled. Run one of the following to install it, then run this script again")
  print("\npip install ExifRead\n\nOR\n\npip3 install ExifRead")
  exit(1)
import logging
import csv

# Setup logging
logging.basicConfig(
    filename="photo_sort.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Setup duplicate logging
DUPLICATES_LOG = "duplicates.csv"

# Configuration
SOURCE_DIR = os.getcwd()
DEST_DIR = os.path.join(SOURCE_DIR, "OrganizedMedia")
CHUNK_SIZE = 8192  # For hashing large files
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".heic", ".gif", ".mp4", ".mov", ".avi", ".mkv")
HASH_ALGORITHM = "sha256"  # Change to "md5" for faster processing if desired

def get_file_hash(filepath):
    """Calculate hash of a file using specified algorithm."""
    if HASH_ALGORITHM == "sha256":
        hasher = hashlib.sha256()
    elif HASH_ALGORITHM == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError("Unsupported hash algorithm")
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing {filepath}: {e}")
        return None

def get_file_date(filepath):
    """Extract date from EXIF (photos), metadata, or modification time."""
    if filepath.suffix.lower() in (".jpg", ".jpeg", ".heic"):
        try:
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f, stop_tag="DateTimeOriginal")
                if "EXIF DateTimeOriginal" in tags:
                    date_str = str(tags["EXIF DateTimeOriginal"])
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass
    # Fallback to modification time for videos or photos without EXIF
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime)
    except Exception as e:
        logging.error(f"Error getting date for {filepath}: {e}")
        return datetime.now()

def create_dest_path(filepath, dest_dir, dup_suffix=None):
    """Determine destination path based on file date, with optional duplicate suffix."""
    date = get_file_date(filepath)
    year = date.strftime("%Y")
    month = date.strftime("%m")
    filename = Path(filepath).name
    if dup_suffix:
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{dup_suffix}{ext}"
    return Path(dest_dir) / year / month / filename

def scan_and_group_files(source_dir):
    """Scan directory and group files by name."""
    file_groups = defaultdict(list)
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(VALID_EXTENSIONS):
                filepath = Path(root) / filename
                file_groups[filename].append(filepath)
    return file_groups

def log_duplicate(keeper, duplicate, dest_path):
    """Log duplicate to CSV."""
    with open(DUPLICATES_LOG, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([str(keeper), str(duplicate), str(dest_path)])

def process_files(file_groups, dest_dir):
    """Process files: deduplicate, rename, and organize."""
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    # Initialize duplicates CSV
    with open(DUPLICATES_LOG, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Keeper", "Duplicate", "Duplicate_Destination"])

    for filename, filepaths in file_groups.items():
        if len(filepaths) == 1:
            # Single file, move to organized structure
            src = filepaths[0]
            dest = create_dest_path(src, dest_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
                logging.info(f"Moved {src} to {dest}")
            except Exception as e:
                logging.error(f"Error moving {src} to {dest}: {e}")
        else:
            # Potential duplicates, verify with hash
            hash_to_paths = defaultdict(list)
            for filepath in filepaths:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_to_paths[file_hash].append(filepath)

            for file_hash, paths in hash_to_paths.items():
                if len(paths) > 1:
                    # Duplicates found, keep one, rename others
                    keeper = paths[0]
                    dest = create_dest_path(keeper, dest_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(keeper), str(dest))
                        logging.info(f"Kept {keeper} at {dest}")
                    except Exception as e:
                        logging.error(f"Error moving {keeper} to {dest}: {e}")

                    for i, dup in enumerate(paths[1:], 1):
                        dup_dest = create_dest_path(dup, dest_dir, f"dup{i}")
                        dup_dest.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            shutil.move(str(dup), str(dup_dest))
                            logging.info(f"Renamed duplicate {dup} to {dup_dest}")
                            log_duplicate(keeper, dup, dup_dest)
                        except Exception as e:
                            logging.error(f"Error moving {dup} to {dup_dest}: {e}")
                else:
                    # Unique file, move to organized structure
                    src = paths[0]
                    dest = create_dest_path(src, dest_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(src), str(dest))
                        logging.info(f"Moved {src} to {dest}")
                    except Exception as e:
                        logging.error(f"Error moving {src} to {dest}: {e}")

def main():
    logging.info(f"Starting photo and video sort and deduplication with {HASH_ALGORITHM}")
    file_groups = scan_and_group_files(SOURCE_DIR)
    logging.info(f"Found {sum(len(paths) for paths in file_groups.values())} files")
    process_files(file_groups, DEST_DIR)
    logging.info("Completed photo and video sort and deduplication")

if __name__ == "__main__":
    main()

