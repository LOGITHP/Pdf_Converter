// State Management
let converterQueue = [];
let compressQueue = [];
let isConverting = false;
let isCompressing = false;

// DOM Elements - Navigation & Global
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const printTemplate = document.getElementById('print-template');
const tabConverter = document.getElementById('tab-converter');
const tabCompressor = document.getElementById('tab-compressor');
const converterContainer = document.getElementById('converter-container');
const compressorContainer = document.getElementById('compressor-container');

// DOM Elements - Converter Queue
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileListContainer = document.getElementById('file-list');
const emptyQueueElement = document.getElementById('empty-queue');
const convertAllBtn = document.getElementById('convert-all-btn');
const downloadAllBtn = document.getElementById('download-all-btn');
const clearAllBtn = document.getElementById('clear-all-btn');

// DOM Elements - Compressor Queue
const compressDropzone = document.getElementById('compress-dropzone');
const compressFileInput = document.getElementById('compress-file-input');
const compressFileList = document.getElementById('compress-file-list');
const compressEmptyQueue = document.getElementById('compress-empty-queue');
const compressAllBtn = document.getElementById('compress-all-btn');
const compressClearBtn = document.getElementById('compress-clear-btn');
const compressDownloadAllBtn = document.getElementById('compress-download-all-btn');
const compressionQuality = document.getElementById('compression-quality');
const qualityValDisplay = document.getElementById('quality-val-display');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTheme();
    setupEventListeners();
    updateConverterUI();
    updateCompressorUI();
});

// Theme Setup
function setupTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Event Listeners
function setupEventListeners() {
    themeToggleBtn.addEventListener('click', toggleTheme);

    // Tabs Navigation
    tabConverter.addEventListener('click', () => switchTab('converter'));
    tabCompressor.addEventListener('click', () => switchTab('compressor'));

    // --- PDF Converter Event Listeners ---
    dropzone.addEventListener('click', (e) => {
        if (e.target === fileInput) return;
        fileInput.click();
    });

    // Prevent the click event from bubbling up to dropzone (resolves recursive explorer dialog loops)
    fileInput.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleConverterFilesSelected(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleConverterFilesSelected(e.target.files);
            fileInput.value = ''; // Reset file input
        }
    });

    convertAllBtn.addEventListener('click', convertAllFiles);
    downloadAllBtn.addEventListener('click', downloadAllFiles);
    clearAllBtn.addEventListener('click', clearAllFiles);

    // --- Compressor Event Listeners ---
    compressDropzone.addEventListener('click', (e) => {
        if (e.target === compressFileInput) return;
        compressFileInput.click();
    });

    // Prevent the click event from bubbling up to compressDropzone
    compressFileInput.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    compressDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        compressDropzone.classList.add('dragover');
    });

    compressDropzone.addEventListener('dragleave', () => {
        compressDropzone.classList.remove('dragover');
    });

    compressDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        compressDropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleCompressFilesSelected(e.dataTransfer.files);
        }
    });

    compressFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleCompressFilesSelected(e.target.files);
            compressFileInput.value = '';
        }
    });

    compressionQuality.addEventListener('input', (e) => {
        qualityValDisplay.textContent = e.target.value + '%';
    });

    compressAllBtn.addEventListener('click', compressAllFiles);
    compressDownloadAllBtn.addEventListener('click', compressDownloadAllFiles);
    compressClearBtn.addEventListener('click', compressClearAllFiles);
}

// Tab Switching logic
function switchTab(tabName) {
    if (tabName === 'converter') {
        tabConverter.classList.add('active');
        tabCompressor.classList.remove('active');
        converterContainer.style.display = 'block';
        compressorContainer.style.display = 'none';
    } else {
        tabConverter.classList.remove('active');
        tabCompressor.classList.add('active');
        converterContainer.style.display = 'none';
        compressorContainer.style.display = 'block';
    }
}

// ----------------------------------------------------
// PDF CONVERTER QUEUE CONTROLLER
// ----------------------------------------------------

function handleConverterFilesSelected(files) {
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const ext = getFileExtension(file.name);

        const fileId = 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        converterQueue.push({
            id: fileId,
            file: file,
            name: file.name,
            size: file.size,
            ext: ext,
            status: 'queued', // queued, converting, completed, failed
            progress: 0,
            pdfBlob: null,
            errorMsg: ''
        });
    }
    updateConverterUI();
}

function updateConverterUI() {
    if (converterQueue.length === 0) {
        emptyQueueElement.style.display = 'flex';
        fileListContainer.style.display = 'none';
        convertAllBtn.disabled = true;
        downloadAllBtn.disabled = true;
        clearAllBtn.disabled = true;
        return;
    }

    emptyQueueElement.style.display = 'none';
    fileListContainer.style.display = 'flex';
    clearAllBtn.disabled = isConverting;

    const hasConvertible = converterQueue.some(item => item.status === 'queued' || item.status === 'failed');
    convertAllBtn.disabled = !hasConvertible || isConverting;

    const hasCompleted = converterQueue.some(item => item.status === 'completed' && item.pdfBlob);
    downloadAllBtn.disabled = !hasCompleted;

    fileListContainer.innerHTML = '';

    converterQueue.forEach(item => {
        const fileItemHtml = `
            <div class="file-item" id="${item.id}">
                <div class="file-icon">${getFileTypeSVG(item.ext)}</div>
                <div class="file-info">
                    <div class="file-name" title="${item.name}">${item.name}</div>
                    <div class="file-meta">
                        <span class="file-type-badge badge-${item.ext}">${item.ext}</span>
                        <span>•</span>
                        <span>${formatBytes(item.size)}</span>
                        ${item.errorMsg ? `<span>•</span><span class="status-failed">${item.errorMsg}</span>` : ''}
                    </div>
                    ${item.status === 'converting' || item.status === 'completed' ? `
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${item.progress}%"></div>
                        </div>
                    ` : ''}
                </div>
                <div class="file-actions">
                    <span class="status-text status-${item.status}">
                        ${item.status === 'queued' ? 'Queued' : ''}
                        ${item.status === 'converting' ? `Converting ${item.progress}%` : ''}
                        ${item.status === 'completed' ? 'Ready' : ''}
                        ${item.status === 'failed' ? 'Failed' : ''}
                    </span>
                    ${item.status === 'completed' ? `
                        <button class="btn btn-secondary btn-sm" onclick="downloadConverterFile('${item.id}')" title="Download PDF">
                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        </button>
                    ` : ''}
                    <button class="remove-btn" onclick="removeConverterFile('${item.id}')" ${isConverting ? 'disabled' : ''} title="Remove">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </div>
        `;
        fileListContainer.insertAdjacentHTML('beforeend', fileItemHtml);
    });
}

window.removeConverterFile = function (id) {
    if (isConverting) return;
    converterQueue = converterQueue.filter(item => item.id !== id);
    updateConverterUI();
};

function clearAllFiles() {
    if (isConverting) return;
    converterQueue = [];
    updateConverterUI();
}

window.downloadConverterFile = function (id) {
    const item = converterQueue.find(f => f.id === id);
    if (item && item.pdfBlob) {
        const url = URL.createObjectURL(item.pdfBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = item.name.substring(0, item.name.lastIndexOf('.')) + '.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 100);
    }
};

async function downloadAllFiles() {
    const completedItems = converterQueue.filter(item => item.status === 'completed' && item.pdfBlob);
    if (completedItems.length === 0) return;

    downloadAllBtn.disabled = true;
    downloadAllBtn.innerHTML = 'Packaging ZIP...';

    try {
        const zip = new JSZip();
        completedItems.forEach(item => {
            const pdfName = item.name.substring(0, item.name.lastIndexOf('.')) + '.pdf';
            zip.file(pdfName, item.pdfBlob);
        });

        const zipBlob = await zip.generateAsync({ type: 'blob' });

        const url = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_pdfs_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 100);
    } catch (e) {
        alert("Error creating ZIP file: " + e.message);
    } finally {
        downloadAllBtn.innerHTML = 'Download All (ZIP)';
        downloadAllBtn.disabled = false;
    }
}

async function convertAllFiles() {
    if (isConverting) return;

    const itemsToConvert = converterQueue.filter(item => item.status === 'queued' || item.status === 'failed');
    if (itemsToConvert.length === 0) return;

    isConverting = true;
    updateConverterUI();

    for (let i = 0; i < itemsToConvert.length; i++) {
        const item = itemsToConvert[i];
        try {
            item.status = 'converting';
            item.progress = 10;
            updateConverterUI();

            const pdfBlob = await performConversion(item);

            item.status = 'completed';
            item.progress = 100;
            item.pdfBlob = pdfBlob;
            item.errorMsg = '';
        } catch (error) {
            console.error(`Error converting ${item.name}:`, error);
            item.status = 'failed';
            item.progress = 0;
            item.errorMsg = error.message || 'Conversion failed';
        }
        updateConverterUI();
    }

    isConverting = false;
    updateConverterUI();
}

async function performConversion(item) {
    const file = item.file;
    const ext = item.ext;

    let htmlContent = '';

    item.progress = 30;
    updateConverterUI();

    if (['docx', 'doc'].includes(ext)) {
        const arrayBuffer = await readFileAsArrayBuffer(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = await renderWord(arrayBuffer);
    } else if (['xlsx', 'xls', 'csv'].includes(ext)) {
        const arrayBuffer = await readFileAsArrayBuffer(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = await renderExcel(arrayBuffer, ext);
    } else if (ext === 'ipynb') {
        const text = await readFileAsText(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = renderNotebook(text);
    } else if (ext === 'md') {
        const text = await readFileAsText(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = renderMarkdown(text);
    } else if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'].includes(ext)) {
        const dataUrl = await readFileAsDataURL(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = renderImage(dataUrl);
    } else if (['py', 'js', 'json', 'css', 'html', 'cpp', 'java', 'go', 'rs', 'cs', 'sh', 'yaml', 'yml', 'xml'].includes(ext)) {
        const text = await readFileAsText(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = renderCode(text, item.name, ext);
    } else if (['txt', 'log'].includes(ext)) {
        const text = await readFileAsText(file);
        item.progress = 50;
        updateConverterUI();
        htmlContent = renderText(text);
    } else {
        throw new Error(`Unsupported file type: .${ext}`);
    }

    item.progress = 70;
    updateConverterUI();

    printTemplate.innerHTML = `<div class="print-page">${htmlContent}</div>`;
    Prism.highlightAllUnder(printTemplate);

    await delay(300);

    item.progress = 85;
    updateConverterUI();

    const cleanFileName = item.name.substring(0, item.name.lastIndexOf('.')) + '.pdf';

    const opt = {
        margin: 10,
        filename: cleanFileName,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['css', 'legacy'] }
    };

    const pdfBlob = await html2pdf().set(opt).from(printTemplate).output('blob');
    printTemplate.innerHTML = '';
    return pdfBlob;
}

// ----------------------------------------------------
// FILE COMPRESSOR QUEUE CONTROLLER
// ----------------------------------------------------

function handleCompressFilesSelected(files) {
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const ext = getFileExtension(file.name);

        if (!['pdf', 'png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
            alert(`File "${file.name}" is not supported for compression. Upload PDFs or images.`);
            continue;
        }

        const fileId = 'comp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        compressQueue.push({
            id: fileId,
            file: file,
            name: file.name,
            originalSize: file.size,
            compressedSize: null,
            ext: ext,
            status: 'queued', // queued, converting, completed, failed
            progress: 0,
            compressedBlob: null,
            errorMsg: ''
        });
    }
    updateCompressorUI();
}

function updateCompressorUI() {
    if (compressQueue.length === 0) {
        compressEmptyQueue.style.display = 'flex';
        compressFileList.style.display = 'none';
        compressAllBtn.disabled = true;
        compressDownloadAllBtn.disabled = true;
        compressClearBtn.disabled = true;
        return;
    }

    compressEmptyQueue.style.display = 'none';
    compressFileList.style.display = 'flex';
    compressClearBtn.disabled = isCompressing;

    const hasCompressible = compressQueue.some(item => item.status === 'queued' || item.status === 'failed');
    compressAllBtn.disabled = !hasCompressible || isCompressing;

    const hasCompleted = compressQueue.some(item => item.status === 'completed' && item.compressedBlob);
    compressDownloadAllBtn.disabled = !hasCompleted;

    compressFileList.innerHTML = '';

    compressQueue.forEach(item => {
        const hasSavings = item.status === 'completed' && item.compressedSize !== null;
        let savingsPercent = 0;
        if (hasSavings && item.originalSize > 0) {
            savingsPercent = Math.round(((item.originalSize - item.compressedSize) / item.originalSize) * 100);
            if (savingsPercent < 0) savingsPercent = 0;
        }

        const fileItemHtml = `
            <div class="file-item" id="${item.id}">
                <div class="file-icon">${getFileTypeSVG(item.ext)}</div>
                <div class="file-info">
                    <div class="file-name" title="${item.name}">${item.name}</div>
                    <div class="file-meta">
                        <span class="file-type-badge badge-${item.ext}">${item.ext}</span>
                        <span>•</span>
                        <span>Original: ${formatBytes(item.originalSize)}</span>
                        ${item.status === 'completed' && item.compressedSize ? `
                            <span>•</span>
                            <span>Compressed: ${formatBytes(item.compressedSize)}</span>
                            ${savingsPercent > 0 ? `<span>•</span><span class="savings-badge">Saved ${savingsPercent}%</span>` : ''}
                        ` : ''}
                        ${item.errorMsg ? `<span>•</span><span class="status-failed">${item.errorMsg}</span>` : ''}
                    </div>
                    ${item.status === 'converting' || item.status === 'completed' ? `
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${item.progress}%"></div>
                        </div>
                    ` : ''}
                </div>
                <div class="file-actions">
                    <span class="status-text status-${item.status}">
                        ${item.status === 'queued' ? 'Queued' : ''}
                        ${item.status === 'converting' ? `Compressing ${item.progress}%` : ''}
                        ${item.status === 'completed' ? 'Done' : ''}
                        ${item.status === 'failed' ? 'Failed' : ''}
                    </span>
                    ${item.status === 'completed' ? `
                        <button class="btn btn-secondary btn-sm" onclick="downloadCompressedFile('${item.id}')" title="Download Compressed File">
                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        </button>
                    ` : ''}
                    <button class="remove-btn" onclick="removeCompressorFile('${item.id}')" ${isCompressing ? 'disabled' : ''} title="Remove">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </div>
        `;
        compressFileList.insertAdjacentHTML('beforeend', fileItemHtml);
    });
}

window.removeCompressorFile = function (id) {
    if (isCompressing) return;
    compressQueue = compressQueue.filter(item => item.id !== id);
    updateCompressorUI();
};

function compressClearAllFiles() {
    if (isCompressing) return;
    compressQueue = [];
    updateCompressorUI();
}

window.downloadCompressedFile = function (id) {
    const item = compressQueue.find(f => f.id === id);
    if (item && item.compressedBlob) {
        const url = URL.createObjectURL(item.compressedBlob);
        const a = document.createElement('a');
        a.href = url;

        const dotIdx = item.name.lastIndexOf('.');
        const nameNoExt = item.name.substring(0, dotIdx);
        const outExt = item.ext === 'pdf' ? 'pdf' : 'jpg';

        a.download = `${nameNoExt}_compressed.${outExt}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 100);
    }
};

async function compressDownloadAllFiles() {
    const completedItems = compressQueue.filter(item => item.status === 'completed' && item.compressedBlob);
    if (completedItems.length === 0) return;

    compressDownloadAllBtn.disabled = true;
    compressDownloadAllBtn.innerHTML = 'Packaging ZIP...';

    try {
        const zip = new JSZip();
        completedItems.forEach(item => {
            const dotIdx = item.name.lastIndexOf('.');
            const nameNoExt = item.name.substring(0, dotIdx);
            const outExt = item.ext === 'pdf' ? 'pdf' : 'jpg';
            const compName = `${nameNoExt}_compressed.${outExt}`;

            zip.file(compName, item.compressedBlob);
        });

        const zipBlob = await zip.generateAsync({ type: 'blob' });

        const url = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compressed_files_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 100);
    } catch (e) {
        alert("Error creating ZIP file: " + e.message);
    } finally {
        compressDownloadAllBtn.innerHTML = 'Download All (ZIP)';
        compressDownloadAllBtn.disabled = false;
    }
}

async function compressAllFiles() {
    if (isCompressing) return;

    const itemsToCompress = compressQueue.filter(item => item.status === 'queued' || item.status === 'failed');
    if (itemsToCompress.length === 0) return;

    isCompressing = true;
    updateCompressorUI();

    const qualityVal = parseInt(compressionQuality.value) / 100;

    for (let i = 0; i < itemsToCompress.length; i++) {
        const item = itemsToCompress[i];
        try {
            item.status = 'converting';
            item.progress = 15;
            updateCompressorUI();

            let compressedBlob;

            if (item.ext === 'pdf') {
                compressedBlob = await runPdfCompression(item, qualityVal);
            } else {
                compressedBlob = await runImageCompression(item, qualityVal);
            }

            item.status = 'completed';
            item.progress = 100;
            item.compressedBlob = compressedBlob;
            item.compressedSize = compressedBlob.size;
            item.errorMsg = '';
        } catch (error) {
            console.error(`Error compressing ${item.name}:`, error);
            item.status = 'failed';
            item.progress = 0;
            item.errorMsg = error.message || 'Compression failed';
        }
        updateCompressorUI();
    }

    isCompressing = false;
    updateCompressorUI();
}

// Perform image compression in canvas
async function runImageCompression(item, quality) {
    return new Promise((resolve, reject) => {
        const file = item.file;
        const reader = new FileReader();

        reader.onload = function (event) {
            const img = new Image();
            img.onload = function () {
                const maxDim = 2048;
                let width = img.width;
                let height = img.height;

                if (width > maxDim || height > maxDim) {
                    if (width > height) {
                        height = Math.round((height * maxDim) / width);
                        width = maxDim;
                    } else {
                        width = Math.round((width * maxDim) / height);
                        height = maxDim;
                    }
                }

                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = width;
                canvas.height = height;

                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, width, height);
                ctx.drawImage(img, 0, 0, width, height);

                item.progress = 75;
                updateCompressorUI();

                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error("Image compression canvas export failed"));
                    }
                }, 'image/jpeg', quality);
            };
            img.onerror = () => reject(new Error("Failed to read image buffer"));
            img.src = event.target.result;
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

// Perform PDF compression by page-rendering to canvas and repacking via jsPDF
async function runPdfCompression(item, quality) {
    const file = item.file;
    const arrayBuffer = await readFileAsArrayBuffer(file);

    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    const loadingTask = pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) });
    const pdf = await loadingTask.promise;

    const jsPDF = (window.jspdf && window.jspdf.jsPDF) || window.jsPDF;
    let doc;

    const totalPages = pdf.numPages;
    const scale = 0.5 + (quality * 1.25);

    for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        item.progress = Math.round(15 + ((pageNum - 1) / totalPages) * 75);
        updateCompressorUI();

        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: scale });

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        await page.render({ canvasContext: context, viewport: viewport }).promise;

        const imgData = canvas.toDataURL('image/jpeg', quality);
        const orientation = viewport.width > viewport.height ? 'l' : 'p';

        if (pageNum === 1) {
            doc = new jsPDF({
                orientation: orientation,
                unit: 'px',
                format: [viewport.width, viewport.height]
            });
        } else {
            doc.addPage([viewport.width, viewport.height], orientation);
        }

        doc.addImage(imgData, 'JPEG', 0, 0, viewport.width, viewport.height);
    }

    item.progress = 95;
    updateCompressorUI();

    const outputBlob = doc.output('blob');
    return outputBlob;
}

// ----------------------------------------------------
// UTILITY FILE READERS & HELPER METHODS
// ----------------------------------------------------

function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsArrayBuffer(file);
    });
}

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsText(file);
    });
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

const delay = ms => new Promise(res => setTimeout(res, ms));

function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Render dynamic colored vector document icon representing file type
function getFileTypeSVG(ext) {
    const defaultColor = '#4b5563';
    const colors = {
        'docx': '#2563eb', 'doc': '#2563eb',
        'xlsx': '#16a34a', 'xls': '#16a34a',
        'ipynb': '#d97706',
        'png': '#db2777', 'jpg': '#db2777', 'jpeg': '#db2777', 'webp': '#db2777', 'gif': '#db2777', 'bmp': '#db2777',
        'md': '#111827',
        'txt': '#4b5563', 'log': '#4b5563',
        'csv': '#0284c7',
        'pdf': '#dc2626'
    };

    let color = colors[ext] || defaultColor;
    if (['py', 'js', 'json', 'css', 'html', 'cpp', 'java', 'go', 'rs', 'cs', 'sh', 'yaml', 'yml', 'xml'].includes(ext)) {
        color = '#7c3aed';
    }

    return `
        <svg viewBox="0 0 24 24" width="32" height="32" stroke="${color}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round" class="file-svg-icon" style="display: block;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
    `;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getPrismLanguageClass(ext) {
    const map = {
        'js': 'language-javascript',
        'jsx': 'language-javascript',
        'ts': 'language-typescript',
        'tsx': 'language-typescript',
        'py': 'language-python',
        'html': 'language-html',
        'css': 'language-css',
        'json': 'language-json',
        'md': 'language-markdown',
        'cpp': 'language-cpp',
        'c': 'language-c',
        'java': 'language-java',
        'cs': 'language-csharp',
        'go': 'language-go',
        'rs': 'language-rust',
        'sh': 'language-bash',
        'bat': 'language-batch',
        'sql': 'language-sql',
        'yaml': 'language-yaml',
        'yml': 'language-yaml',
        'xml': 'language-xml'
    };
    return map[ext] || 'language-none';
}

// Format Parsers - Word Document
async function renderWord(arrayBuffer) {
    try {
        const result = await mammoth.convertToHtml({ arrayBuffer: arrayBuffer });
        if (!result.value || result.value.trim() === '') {
            return `<div class="word-print"><p style="color: #666; font-style: italic;">Empty Word document.</p></div>`;
        }
        return `<div class="word-print">${result.value}</div>`;
    } catch (e) {
        throw new Error("Mammoth.js failed parsing docx: " + e.message);
    }
}

// Format Parsers - Excel & CSV
async function renderExcel(arrayBuffer, ext) {
    try {
        const data = new Uint8Array(arrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        let html = '<div class="excel-print">';

        workbook.SheetNames.forEach((sheetName, index) => {
            const worksheet = workbook.Sheets[sheetName];
            const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:A1');
            const isEmpty = !worksheet['!ref'] || (range.s.r === range.e.r && range.s.c === range.e.c && !worksheet[XLSX.utils.encode_cell(range.s)]);

            const pageBreakClass = index > 0 ? 'page-break' : '';
            html += `<div class="sheet-container ${pageBreakClass}">`;
            html += `<h2>Sheet: ${sheetName}</h2>`;

            if (isEmpty) {
                html += `<p style="color: #666; font-style: italic;">Empty sheet.</p>`;
            } else {
                const tableHtml = XLSX.utils.sheet_to_html(worksheet, {
                    header: '',
                    footer: ''
                });
                html += tableHtml;
            }
            html += '</div>';
        });

        html += '</div>';
        return html;
    } catch (e) {
        throw new Error("SheetJS failed parsing spreadsheet: " + e.message);
    }
}

// Format Parsers - Jupyter Notebook
function renderNotebook(ipynbText) {
    try {
        const notebook = JSON.parse(ipynbText);
        let html = '<div class="ipynb-print">';
        html += `<h2 style="font-family: 'Outfit', sans-serif; border-bottom: 2px solid #047857; padding-bottom: 5px; margin-bottom: 20px;">Jupyter Notebook</h2>`;

        const cells = notebook.cells || [];
        if (cells.length === 0) {
            html += '<p style="color: #666; font-style: italic;">Empty Notebook</p>';
        }

        cells.forEach((cell) => {
            const cellType = cell.cell_type;
            const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source || '';
            html += '<div class="ipynb-cell">';

            if (cellType === 'markdown') {
                const mdHtml = marked.parse(source);
                html += `<div class="ipynb-markdown">${mdHtml}</div>`;
            } else if (cellType === 'code') {
                const executionCount = cell.execution_count !== null && cell.execution_count !== undefined ? cell.execution_count : ' ';
                html += `<div class="ipynb-cell-prompt">In [${executionCount}]:</div>`;

                const escapedCode = escapeHtml(source);
                html += `<pre class="ipynb-input"><code class="language-python">${escapedCode}</code></pre>`;

                const outputs = cell.outputs || [];
                if (outputs.length > 0) {
                    outputs.forEach(output => {
                        if (output.output_type === 'stream') {
                            const text = Array.isArray(output.text) ? output.text.join('') : output.text || '';
                            html += `<pre class="ipynb-output">${escapeHtml(text)}</pre>`;
                        } else if (output.output_type === 'execute_result' || output.output_type === 'display_data') {
                            const data = output.data || {};
                            if (data['image/png']) {
                                const base64Img = data['image/png'].replace(/\n/g, '');
                                html += `<div class="ipynb-output-image"><img src="data:image/png;base64,${base64Img}" /></div>`;
                            } else if (data['text/plain']) {
                                const text = Array.isArray(data['text/plain']) ? data['text/plain'].join('') : data['text/plain'] || '';
                                html += `<pre class="ipynb-output">${escapeHtml(text)}</pre>`;
                            }
                        } else if (output.output_type === 'error') {
                            const traceback = Array.isArray(output.traceback) ? output.traceback.join('\n') : output.traceback || '';
                            const cleanTraceback = traceback.replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
                            html += `<pre class="ipynb-output ipynb-error" style="color: #dc2626 !important; border-left: 4px solid #dc2626;">${escapeHtml(cleanTraceback)}</pre>`;
                        }
                    });
                }
            }
            html += '</div>';
        });

        html += '</div>';
        return html;
    } catch (e) {
        throw new Error("Invalid Jupyter Notebook format: " + e.message);
    }
}

// Format Parsers - Markdown
function renderMarkdown(mdText) {
    try {
        const mdHtml = marked.parse(mdText);
        return `<div class="md-print">${mdHtml}</div>`;
    } catch (e) {
        throw new Error("Marked.js failed parsing Markdown: " + e.message);
    }
}

// Format Parsers - Image
function renderImage(dataUrl) {
    return `<div class="image-print"><img src="${dataUrl}" alt="Converted Image" /></div>`;
}

// Format Parsers - Code
function renderCode(codeText, filename, ext) {
    const langClass = getPrismLanguageClass(ext);
    const escapedCode = escapeHtml(codeText);
    return `
        <div class="code-print">
            <div class="code-print-header">${filename}</div>
            <pre class="code-print-pre"><code class="${langClass}">${escapedCode}</code></pre>
        </div>
    `;
}

// Format Parsers - Plain Text
function renderText(text) {
    const escapedText = escapeHtml(text);
    return `<div class="text-print"><pre style="margin: 0; white-space: pre-wrap; word-break: break-all; font-family: 'JetBrains Mono', monospace;">${escapedText}</pre></div>`;
}
