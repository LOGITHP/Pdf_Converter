# Universal Document Converter & PDF Toolkit

A professional, high-performance Universal Document Converter and PDF editing toolkit. Built with a **React + Tailwind CSS frontend** and a **FastAPI (Python) backend**, this application is designed for rapid document processing, compression, and advanced PDF manipulations.



---

## 🌟 Advantages of the Application
- **Privacy & Security**: All file processing happens entirely in-memory and in secure staging directories. Files are never sent to external third-party APIs.
- **Universal Format Support**: Convert Office documents (Word, Excel, PPT), Code snippets, Jupyter Notebooks, Markdown, and Images directly into PDFs or other formats.
- **Advanced PDF Toolkit**: Effortlessly Merge, Split, Rotate, Watermark, and Encrypt/Decrypt PDF documents.
- **File Compression**: Intelligently compress images and PDFs with adjustable quality levels to save space.
- **Docker Ready**: Fully containerized environment ensuring that complex system dependencies (like LibreOffice, FFmpeg, Ghostscript) work flawlessly in the cloud without complex manual installation.

---

## 💻 Local Setup Instructions

The files in the GitHub repository are **100% sufficient** to run the app locally, provided you use **Docker**. Docker automatically installs all the heavy system binaries (LibreOffice, Ghostscript, FFmpeg).

### Method 1: Docker Setup (Recommended & Fully Supported by GitHub Repo)
If you have Docker Desktop installed, you don't need to manually install Node, Python, or any system binaries.
1. Build the Docker image locally:
   ```bash
   docker build -t universal-converter .
   ```
2. Run the Docker container:
   ```bash
   docker run -p 10000:10000 universal-converter
   ```
3. Open your browser to `http://localhost:10000`.

### Method 2: Native Python Setup (Requires Additional Files)
If you want to run the app natively on Windows using standard Python and Node.js without Docker, the GitHub repository is **not enough** on its own because the native Windows binaries (`.exe` engines) are excluded from the repository to save space.

*Note: For this native setup, please contact me for the `download_runtimes.py` script or the full repository drive link containing the `runtime/` folder.*

1. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
2. **Backend Setup & Running**:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
   The app will open automatically at `http://localhost:8000`.

---

## ☁️ Render Deployment Guide (Docker)

The application is fully configured to be deployed on Render using Docker. This ensures all heavy system binaries (LibreOffice, Tesseract, etc.) are installed perfectly in the cloud.

### Step-by-Step Deployment:
1. **Clone & Push**: Ensure this repository is pushed to your own GitHub account.
2. **Log into Render**: Go to [Render.com](https://render.com) and log in with your GitHub account.
3. **Create a New Web Service**:
   - Click the **"New"** button at the top right and select **"Web Service"**.
   - Connect your GitHub repository containing this project.
4. **Configure the Service**:
   - **Name**: Choose a name for your app.
   - **Region**: Choose the region closest to your users.
   - **Branch**: `main` (or whichever branch you are using).
   - **Runtime**: Render might default to `Python` because of the `requirements.txt` file. **You MUST change the Runtime to `Docker`**. This tells Render to look for the `Dockerfile`.
   - **Build Command**: Leave blank (Docker handles this).
   - **Start Command**: Leave blank (Docker handles this via the `CMD` instruction).
5. **Select Instance Type**: Choose the Free tier (or a paid tier if you need more RAM for heavy document conversions).
6. **Deploy**: Click **"Create Web Service"**.
   
Render will now build the Docker image (which includes building the React frontend and installing Linux system dependencies). Once the build succeeds, it will deploy the service and provide you with a live URL (e.g., `https://your-app.onrender.com`).

*Note on Free Tier: If your app is inactive for 15 minutes, Render will spin down the server. When you open the link again, it may take 1-2 minutes to "cold start" and load the webpage.*
