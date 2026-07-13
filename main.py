import uvicorn
import webbrowser
import socket
import os
import sys
import threading
import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8")
    ]
)
logger = logging.getLogger("server_main")

# Import backend endpoints and utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.api.endpoints import router as api_router
from backend.utils.cleanup import run_cleanup, ensure_directories

app = FastAPI(
    title="Universal Offline Document Converter API",
    description="Local offline document conversion and compression API.",
    version="2.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In local offline environment, wildcard is secure and easy for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include APIs
app.include_router(api_router)

# Mount frontend assets if built
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "UniversalConverter"}

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Track background initialization state
IS_INITIALIZING = False
INIT_LOGS = []

@app.get("/api/init_status")
def get_init_status():
    """Endpoint for frontend to check if a local download initialization is happening."""
    return {"initializing": IS_INITIALIZING, "logs": INIT_LOGS[-5:] if INIT_LOGS else []}

def auto_initialize_local():
    """Automatically downloads engines locally if running on Windows and runtime folder is missing."""
    global IS_INITIALIZING
    if sys.platform != "win32":
        return
        
    app_root = os.path.dirname(os.path.abspath(__file__))
    runtime_dir = os.path.join(app_root, "runtime")
    
    # If runtime directory doesn't exist or is completely empty, trigger first-time download
    if not os.path.exists(runtime_dir) or not os.listdir(runtime_dir):
        IS_INITIALIZING = True
        logger.info("First-time local run detected. Missing runtime engines. Starting auto-downloader...")
        try:
            import download_runtimes
            # We intercept stdout to give frontend some logs if we want, or just let it run.
            download_runtimes.run_all_setups()
        except Exception as e:
            logger.error(f"Auto-initialization failed: {e}")
        finally:
            IS_INITIALIZING = False
            logger.info("Auto-initialization complete.")

def cleanup_daemon():
    """Background daemon thread to clean old temp/output files every 10 mins."""
    logger.info("Temporary files cleanup daemon started.")
    while True:
        try:
            run_cleanup(force_all=False)
        except Exception as e:
            logger.error(f"Error running scheduled cleanup: {e}")
        time.sleep(600) # run every 10 minutes

@app.on_event("startup")
def startup_event():
    # Setup directories
    ensure_directories()
    # Initial clean of old temp files
    run_cleanup(force_all=True)
    
    # Start auto-downloader thread if necessary (runs in background)
    t_init = threading.Thread(target=auto_initialize_local, daemon=True)
    t_init.start()
    
    # Start background cleanup thread
    t = threading.Thread(target=cleanup_daemon, daemon=True)
    t.start()

@app.on_event("shutdown")
def shutdown_event():
    # Clean up all temp/output files on shutdown
    logger.info("Cleaning up workspace folders on server shutdown.")
    try:
        run_cleanup(force_all=True)
    except Exception as e:
        logger.error(f"Shutdown cleanup failed: {e}")

# Check if front-end is compiled, serve it, or show a fallback guide
if os.path.exists(FRONTEND_DIST_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")
else:
    logger.warning(f"Frontend built assets not found at: {FRONTEND_DIST_DIR}. Serving development fallback screen.")
    
    @app.get("/", response_class=HTMLResponse)
    def index_fallback():
        return """<!DOCTYPE html>
<html>
<head>
    <title>Universal Offline Converter - Developer Mode</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px 20px; }
        .card { background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        h1 { color: #34d399; margin-top: 0; }
        code { background: #0f172a; padding: 4px 8px; border-radius: 4px; color: #f472b6; font-family: monospace; font-size: 0.95em; }
        ol { padding-left: 20px; line-height: 1.8; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Universal Offline Converter (Local API Server Running)</h1>
        <p>The backend REST API is running. However, the React frontend distribution folder was not detected.</p>
        <p><strong>To run the application in Development Mode:</strong></p>
        <ol>
            <li>Open a terminal in the <code>frontend/</code> folder.</li>
            <li>Run <code>npm install</code> to set up development libraries.</li>
            <li>Run <code>npm run dev</code> to boot the hot-reloading web page.</li>
            <li>Open your browser to the URL displayed by Vite (usually <code>http://localhost:5173</code>).</li>
        </ol>
        <p><strong>To compile the production build:</strong></p>
        <ol>
            <li>Run <code>npm run build</code> in the <code>frontend/</code> directory.</li>
            <li>Restart this Python server. It will automatically detect <code>frontend/dist/</code> and serve it directly on port 8000!</li>
        </ol>
    </div>
</body>
</html>"""

def run_server():
    port = 8000
    while port < 8010:
        if not is_port_in_use(port):
            break
        logger.info(f"Port {port} is occupied. Trying next port...")
        port += 1
        
    logger.info(f"Starting server on http://localhost:{port}")
    
    # Auto-open browser in a separate thread so it doesn't block startup
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    run_server()
