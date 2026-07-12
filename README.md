# AeroPDF Universal: Offline Document Converter & PDF Toolkit

AeroPDF Universal is a professional, privacy-first, offline Universal Document Converter and PDF editing toolkit. The application runs entirely on your local machine using a **FastAPI backend** (Python) and a **React + Tailwind CSS frontend** served locally. 

Files are never uploaded to the cloud, ensuring absolute confidentiality, maximum security, and high performance.

---

## 🌟 Key Features

1. **Document Conversion**:
   - **Office Formats**: Converts Word (`.docx`, `.doc`, `.odt`), Excel (`.xlsx`, `.xls`, `.ods`, `.csv`), and PowerPoint (`.pptx`, `.ppt`, `.odp`) to PDF, HTML, or text formats.
   - **Jupyter Notebooks**: Converts `.ipynb` files to PDF, HTML, Markdown, or raw Python, complete with syntax highlighting and base64 embedded graphs.
   - **Source Code**: Renders programming source files (`.py`, `.js`, `.json`, `.cpp`, `.java`, etc.) into beautifully styled PDFs with line numbers and Pygments syntax highlighting.
   - **Markdown & Text**: Transforms Markdown (`.md`) or plain logs (`.txt`, `.log`) into clear PDF or HTML views.
   - **Images**: Scales and wraps image files (`.png`, `.jpg`, `.webp`, `.heic`) into standard A4 PDF pages.

2. **File Compression**:
   - **Image Compressor**: Downscales resolution and optimizes quality levels (10% to 100%) for JPG, PNG, and WebP assets.
   - **PDF Compressor**: Reduces PDF sizes by executing structural optimization, image downsampling, and metadata clearing.

3. **PDF Editing Toolkit**:
   - **Merge**: Combines multiple PDF files in order into a single document.
   - **Split**: Extracts pages of a PDF into individual page files.
   - **Rotate**: Rotates PDF page views (90°, 180°, 270°).
   - **Watermark**: Injects customizable text watermarks diagonally across pages with custom opacity.
   - **Encrypt & Decrypt**: Protects PDFs with password protection or removes password locks.

4. **Local OCR (Text Recognition)**:
   - Recognizes text within scans or images using local Tesseract OCR and generates searchable PDF documents.

5. **Metadata Engine**:
   - View, extract, or edit EXIF metadata and PDF description tags (Author, Creator, Keywords, Copyright) offline.

---

## ⚙️ System Dependencies

For high-fidelity conversions and advanced features, the application dynamically scans your system PATH:
- **LibreOffice Headless**: Needed for high-fidelity conversion of Microsoft Office files. If missing, the app falls back to basic Python library layout parsers (Mammoth & python-docx).
- **Tesseract OCR**: Needed to extract text from images and compile searchable PDFs. If missing, OCR functions will display fallback alerts in the UI.

---

## 📂 Project Structure

```
UniversalConverter/
├── backend/
│   ├── api/            # FastAPI REST endpoints
│   ├── router/         # File type conversion router
│   ├── workers/        # Asynchronous job manager queue
│   ├── converters/     # Specific file engines (pdf, office, notebook, code, etc.)
│   ├── utils/          # System checking and file cleanup utilities
│   ├── temp/           # Intermediate staging files
│   └── output/         # Completed conversion downloads
├── frontend/
│   ├── src/            # React + Tailwind components
│   └── dist/           # Compiled production static assets
├── tests/              # Backend and routing unit tests
├── requirements.txt    # Python package requirements
└── main.py             # Server launcher script
```

---

## 🚀 Local Setup and Startup

### 1. Python Server Dependencies
Install python packages from the root workspace folder:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Run the root launcher script:
```bash
python main.py
```
This script will:
- Initialize the FastAPI server on port 8000 (or next available).
- Start a background cleanup daemon to purge intermediate temp files.
- Automatically serve the React static assets from `frontend/dist/`.
- Open your default web browser automatically to `http://localhost:8000`.

### 3. Developer Mode (Frontend Hot Reloading)
To modify the React user interface with live reloading:
- Navigate to the frontend directory:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- Open `http://localhost:5173` in your browser. The frontend automatically routes its requests to the FastAPI backend running on port 8000.
- When done, compile the final production build:
  ```bash
  npm run build
  ```

---

## 🛡️ Security & Privacy
- **100% Local**: No network requests are made outside your machine.
- **Zero Database**: Conversions are processed in-memory and in staging folders.
- **Self-Cleaning**: Staging folders are swept clean periodically and upon server shutdown.
