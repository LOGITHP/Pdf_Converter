import shutil
import os
import subprocess
import sys

def get_libreoffice_path():
    # 1. Check if in PATH
    path = shutil.which("soffice") or shutil.which("libreoffice")
    if path:
        return path

    # 2. Check common OS locations
    if sys.platform == "win32":
        common_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    elif sys.platform == "darwin":
        common_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    elif sys.platform.startswith("linux"):
        common_paths = [
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
            "/usr/local/bin/libreoffice"
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    return None

def get_tesseract_path():
    # 1. Check if in PATH
    path = shutil.which("tesseract")
    if path:
        return path

    # 2. Check common OS locations
    if sys.platform == "win32":
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), r"AppData\Local\Tesseract-OCR\tesseract.exe")
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    return None

def check_tesseract_availability():
    path = get_tesseract_path()
    if not path:
        return False
    try:
        # Run a version check
        result = subprocess.run([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        return "tesseract" in result.stdout.lower()
    except Exception:
        return False

def check_libreoffice_availability():
    path = get_libreoffice_path()
    if not path:
        return False
    try:
        # Run help output check
        result = subprocess.run([path, "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        return result.returncode == 0
    except Exception:
        return False

def get_system_diagnostics():
    return {
        "os": sys.platform,
        "python_version": sys.version.split(" ")[0],
        "engines": {
            "libreoffice": {
                "available": check_libreoffice_availability(),
                "path": get_libreoffice_path()
            },
            "tesseract": {
                "available": check_tesseract_availability(),
                "path": get_tesseract_path()
            },
            "pymupdf": {
                "available": True,  # Will be imported directly in python env
                "path": "Python Package"
            },
            "pillow": {
                "available": True,
                "path": "Python Package"
            }
        }
    }
