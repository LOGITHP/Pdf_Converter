# ==========================================
# Phase 1: Compile React Frontend
# ==========================================
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ==========================================
# Phase 2: Run FastAPI Python Environment
# ==========================================
FROM python:3.12-slim
WORKDIR /app

# Install all 7 core engine binaries natively on Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    tesseract-ocr \
    ghostscript \
    poppler-utils \
    imagemagick \
    pandoc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy React compiled distribution assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy backend files and root runner
COPY backend/ /app/backend/
COPY main.py /app/main.py

# Render exposes the dynamic PORT environment variable.
# We bind the Uvicorn server to 0.0.0.0 and PORT.
EXPOSE 10000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
