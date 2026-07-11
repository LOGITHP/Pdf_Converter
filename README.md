# AeroPDF: Client-Side PDF Converter and Compressor

AeroPDF is a premium, client-side web application designed to convert and compress documents locally in the browser. Because all processing occurs directly within the client environment, files are never uploaded to a remote server. This architecture guarantees absolute data privacy, rapid conversion speeds, and offline functionality.

The application has no system dependencies (such as Microsoft Office, LibreOffice, or other native runtime environments) and is fully compatible with Windows, Linux, macOS, Android, and iOS.

---

## Technical Specifications and Features

### 1. Document Converter
AeroPDF converts several common file formats into high-fidelity PDF documents:
* **Microsoft Word (DOCX, DOC)**: Parses document elements and formats locally to render readable HTML.
* **Microsoft Excel (XLSX, XLS)**: Generates structured, clean tables for each worksheet, separating tabs with explicit page breaks.
* **Jupyter Notebooks (IPYNB)**: Renders markdown notes, input source cells with Python syntax highlighting, standard outputs, and graphical plots (such as Matplotlib/Seaborn figures represented as base64 images).
* **Markdown (MD)**: Parses standard markdown elements into styled, reader-oriented document layouts.
* **Source Code (PY, JS, JSON, CSS, HTML, etc.)**: Highlights code syntax using Prism.js with automatic line-wrapping to prevent page clipping.
* **CSV Files**: Decodes structured data grids into styled tables with borders and padded cells.
* **Plain Text (TXT, LOG)**: Formats logs and raw text into clean monospace document viewports.
* **Images (PNG, JPG, JPEG, WEBP, BMP)**: Scales images to fit standard A4 paper dimensions.

### 2. File Compressor
AeroPDF optimizes image and PDF file sizes locally:
* **Image Compression (JPG, PNG, WEBP)**: Redraws uploaded images to canvas viewports, restricts maximum dimensions to 2048px to prevent browser memory exhaustion, and exports them to JPEG format at a user-defined compression quality (ranging from 10% to 100%). Transparent PNG assets are automatically overlayed on a white background to avoid rendering artifacts.
* **PDF Compression**: Extracts pages from an uploaded PDF, renders them individually to canvas elements using PDF.js while maintaining original layout aspect ratios, applies JPEG compression, and compiles the compressed pages into a new PDF document.
* **Real-time Metrics**: Displays the original size, the optimized size, and the exact percentage of storage saved.

---

## Local Setup and Installation

AeroPDF can run by opening the index.html file directly in any modern browser, or by serving it locally. Serving the files ensures consistent caching behavior and makes it easy to share the tool across a local network.

### Option A: Using the Python Server (Recommended)
Run the built-in python script to launch the local web server:
```bash
python server.py
```
This script starts a local server on port 8000 (or the next available port) and automatically opens the application in your default browser.

### Option B: Using Node.js
Alternatively, serve the static workspace directory using npm:
```bash
npx serve .
```

---

## Deployment and Hosting

Because AeroPDF is a static client-side application, it does not require a database or backend host. You can host it on any static hosting platform.

### Hosting on GitHub Pages
1. Initialize a git repository and commit your files:
   ```bash
   git init
   git add .
   git commit -m "Initial release of AeroPDF"
   ```
2. Create a repository on GitHub and push your local commits.
3. In your GitHub repository:
   * Go to **Settings** > **Pages**.
   * Under **Build and deployment**, select **Deploy from a branch**.
   * Select your deployment branch (e.g., `main` or `master`) and directory `/ (root)`.
   * Click **Save**.
4. The application will be live at `https://<username>.github.io/<repository-name>/` in a few minutes.

---

## Core Libraries Used
* **PDF Generation**: html2pdf.js (bundles html2canvas and jsPDF)
* **Word Processing**: Mammoth.js (client-side DOCX parser)
* **Spreadsheet Processing**: SheetJS (xlsx.full.min.js)
* **PDF Processing**: PDF.js (Mozilla PDF reader engine)
* **Syntax Highlighting**: Prism.js (with Autoloader plugin)
* **Markdown Parsing**: Marked.js
* **Batch Zipping**: JSZip (client-side ZIP compiler)
