# Universal Document Converter & PDF Toolkit

A professional, high-performance Universal Document Converter and PDF editing toolkit. Built with a **React + Tailwind CSS frontend** and a **FastAPI (Python) backend**, this application is designed for rapid document processing, compression, and advanced PDF manipulations.

**Note**: *Contact me for the files to set up locally or for the full repository drive link.*

---

## 🌟 Advantages of the Application
- **Privacy & Security**: All file processing happens entirely in-memory and in secure staging directories. Files are never sent to external third-party APIs.
- **Universal Format Support**: Convert Office documents (Word, Excel, PPT), Code snippets, Jupyter Notebooks, Markdown, and Images directly into PDFs or other formats.
- **Advanced PDF Toolkit**: Effortlessly Merge, Split, Rotate, Watermark, and Encrypt/Decrypt PDF documents.
- **File Compression**: Intelligently compress images and PDFs with adjustable quality levels to save space.
- **Docker Ready**: Fully containerized environment ensuring that complex system dependencies (like LibreOffice, FFmpeg, Ghostscript) work flawlessly in the cloud without complex manual installation.

---

## 💻 Local Setup Instructions

If you have the local setup files, follow these instructions to run the application on your computer:

### 1. Requirements
- Python 3.10+
- Node.js v18+

### 2. Frontend Setup
Navigate to the frontend folder, install dependencies, and build the production assets:
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Backend Setup & Running
Install the required Python packages and launch the FastAPI server:
```bash
pip install -r requirements.txt
python main.py
```
This script will:
- Initialize the FastAPI server on port 8000.
- Automatically serve the React static assets from `frontend/dist/`.
- Open your default web browser automatically to `http://localhost:8000`.

*(Note: For high-fidelity Word document conversions and media processing locally, you must run the `download_runtimes.py` script to fetch local `.exe` binaries, which are automatically omitted from cloud deployments).*

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
