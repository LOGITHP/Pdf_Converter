import os
import time
import shutil
import logging

logger = logging.getLogger("cleanup")

# Root folders for temp and output
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BACKEND_DIR, "temp")
OUTPUT_DIR = os.path.join(BACKEND_DIR, "output")

def ensure_directories():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Create logs dir too
    os.makedirs(os.path.join(BACKEND_DIR, "logs"), exist_ok=True)

def clean_directory(directory, max_age_seconds=3600):
    """Deletes files in a directory that are older than max_age_seconds."""
    if not os.path.exists(directory):
        return
    
    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            # Skip hidden files
            if filename.startswith('.'):
                continue
            
            # Check modification time
            if os.path.isfile(file_path) or os.path.islink(file_path):
                if os.stat(file_path).st_mtime < now - max_age_seconds:
                    os.remove(file_path)
            elif os.path.isdir(file_path):
                if os.stat(file_path).st_mtime < now - max_age_seconds:
                    shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")

def run_cleanup(force_all=False):
    """Cleans up temporary files. If force_all is True, ignores max_age."""
    ensure_directories()
    age = 0 if force_all else 3600
    clean_directory(TEMP_DIR, age)
    clean_directory(OUTPUT_DIR, age)
