import axios from 'axios';

// Detect local API server port dynamically
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') return 'http://127.0.0.1:8000';
  // If we are in dev mode (usually localhost:5173), fallback to localhost:8000
  if (window.location.port === '5173' || window.location.port === '3000') {
    return 'http://127.0.0.1:8000';
  }
  // In production, backend and frontend run on the same port
  return '';
};

const API_BASE = getApiBaseUrl();

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60 seconds
});

export const api = {
  // 0. Get initialization status (first time local run)
  getInitStatus: async () => {
    try {
      const res = await client.get('/api/init_status');
      return res.data;
    } catch (e) {
      return { initializing: false, logs: [] };
    }
  },

  // 1. Get system engine health diagnostics
  getStatus: async () => {
    const res = await client.get('/api/status');
    return res.data;
  },

  // 2. Submit conversion job
  convertFile: async (file, toExt, ocr = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('to_ext', toExt);
    formData.append('ocr', ocr ? 'true' : 'false');
    
    const res = await client.post('/api/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data; // { job_id: '...', status: 'queued' }
  },

  // 3. Submit compression job
  compressFile: async (file, quality = 0.6) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('quality', quality.toString());
    
    const res = await client.post('/api/compress', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data; // { job_id: '...', status: 'queued' }
  },

  // 4. PDF Tools: Merge
  pdfMerge: async (files) => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const res = await client.post('/api/pdf/merge', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // 5. PDF Tools: Edit (Split, Rotate, Watermark, Encrypt)
  pdfEdit: async (file, operation, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('operation', operation);
    if (options.watermark_text) formData.append('watermark_text', options.watermark_text);
    if (options.password) formData.append('password', options.password);
    if (options.rotation_angle) formData.append('rotation_angle', options.rotation_angle.toString());
    
    const res = await client.post('/api/pdf/edit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // 6. Poll job status/progress
  getJobStatus: async (jobId) => {
    const res = await client.get(`/api/jobs/${jobId}`);
    return res.data;
  },

  // 7. Get file download link
  getDownloadUrl: (filename) => {
    if (!filename) return '#';
    return `${API_BASE}/api/download/${filename}`;
  }
};
