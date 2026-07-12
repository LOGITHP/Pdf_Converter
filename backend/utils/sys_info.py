import os
import sys
import shutil

def get_app_root() -> str:
    """Resolves the root directory of the application, safe for script and compiled modes."""
    if getattr(sys, 'frozen', False):
        # Compiled executable (e.g. PyInstaller)
        return os.path.dirname(sys.executable)
    # Developer source mode
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_engine_path(engine_name: str) -> str:
    """
    Returns the absolute path to the requested bundled engine.
    - On Windows, it checks ONLY the local runtime/ folder.
    - On Linux/macOS (Render cloud), it checks the local runtime/ folder first,
      falling back to the global system PATH (shutil.which) for container-level compatibility.
    """
    app_root = get_app_root()
    is_win = sys.platform == "win32"
    
    # Engine relative search structures for Windows and generic OS
    paths = {
        "libreoffice": [
            "runtime/libreoffice/program/soffice.exe" if is_win else "runtime/libreoffice/program/soffice"
        ],
        "tesseract": [
            "runtime/tesseract/tesseract.exe" if is_win else "runtime/tesseract/tesseract",
            "runtime/tesseract/bin/tesseract"
        ],
        "ghostscript": [
            "runtime/ghostscript/gswin64c.exe" if is_win else "runtime/ghostscript/gs"
        ],
        "poppler": [
            "runtime/poppler/bin/pdftoppm.exe" if is_win else "runtime/poppler/bin/pdftoppm",
            "runtime/poppler/pdftoppm"
        ],
        "imagemagick": [
            "runtime/imagemagick/magick.exe" if is_win else "runtime/imagemagick/magick"
        ],
        "pandoc": [
            "runtime/pandoc/pandoc.exe" if is_win else "runtime/pandoc/pandoc"
        ],
        "ffmpeg": [
            "runtime/ffmpeg/ffmpeg.exe" if is_win else "runtime/ffmpeg/ffmpeg",
            "runtime/ffmpeg/bin/ffmpeg",
            "runtime/ffmpeg/bin/ffmpeg.exe"
        ]
    }
    
    candidates = paths.get(engine_name.lower(), [])
    for rel in candidates:
        abs_path = os.path.normpath(os.path.join(app_root, rel))
        if os.path.exists(abs_path):
            return abs_path
            
    # If not found in local runtime, check global system path ONLY on non-Windows platforms (e.g. Render cloud containers)
    if not is_win:
        system_names = {
            "libreoffice": "soffice",
            "tesseract": "tesseract",
            "ghostscript": "gs",
            "poppler": "pdftoppm",
            "imagemagick": "magick",
            "pandoc": "pandoc",
            "ffmpeg": "ffmpeg"
        }
        name = system_names.get(engine_name.lower())
        if name:
            sys_path = shutil.which(name)
            # ImageMagick fallback name
            if not sys_path and engine_name.lower() == "imagemagick":
                sys_path = shutil.which("convert")
            if sys_path:
                return sys_path
                
    return None

def get_system_diagnostics() -> dict:
    """
    Diagnostics scan restricted ONLY to the bundled runtime directory on Windows,
    and falls back to system PATH on Linux/macOS for cloud deployment.
    """
    engines_list = ["libreoffice", "tesseract", "ghostscript", "poppler", "imagemagick", "pandoc", "ffmpeg"]
    engines_status = {}
    corrupted = False
    
    for engine in engines_list:
        path = get_engine_path(engine)
        available = path is not None
        if not available:
            corrupted = True
        
        # Strip absolute prefix path for clean logs/UI representation
        display_name = "Missing from bundled runtime"
        if path:
            app_root = get_app_root()
            if path.startswith(app_root):
                display_name = os.path.relpath(path, app_root)
            else:
                display_name = f"System PATH ({path})"
            
        engines_status[engine] = {
            "available": available,
            "path": display_name
        }
        
    return {
        "os": sys.platform,
        "python_version": sys.version.split(" ")[0],
        "app_root": get_app_root(),
        "corrupted": corrupted,
        "engines": engines_status
    }
