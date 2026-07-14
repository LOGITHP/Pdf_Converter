import React, { useState, useEffect } from 'react';
import { 
  FileText, ShieldCheck, Sun, Moon, Sparkles, Files, 
  Layers, Lock, RotateCw, PenTool, Columns, HelpCircle,
  FolderOpen, AlertCircle, CheckCircle2, Trash2, Download, Play, RefreshCw
} from 'lucide-react';
import { api } from './services/api';
import DragDropZone from './components/DragDropZone';
import EngineStatus from './components/EngineStatus';
import ConversionQueue from './components/ConversionQueue';

export default function App() {
  const [activeTab, setActiveTab] = useState('converter'); // 'converter', 'compressor', 'pdf-tools'
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [diagnostics, setDiagnostics] = useState(null);
  const [diagLoading, setDiagLoading] = useState(true);
  const [initStatus, setInitStatus] = useState({ initializing: true, logs: [] });
  
  // State Queues
  const [converterQueue, setConverterQueue] = useState([]);
  const [isConverterProcessing, setIsConverterProcessing] = useState(false);
  
  const [compressorQueue, setCompressorQueue] = useState([]);
  const [isCompressorProcessing, setIsCompressorProcessing] = useState(false);
  const [compressionQuality, setCompressionQuality] = useState(60); // 10% - 100%
  
  // PDF Tools state
  const [pdfFiles, setPdfFiles] = useState([]);
  const [pdfOp, setPdfOp] = useState('merge'); // 'merge', 'split', 'rotate', 'watermark', 'encrypt'
  const [pdfWatermarkText, setPdfWatermarkText] = useState('CONFIDENTIAL');
  const [pdfPassword, setPdfPassword] = useState('');
  const [pdfRotation, setPdfRotation] = useState(90);
  const [pdfToolResult, setPdfToolResult] = useState(null);
  const [isPdfToolProcessing, setIsPdfToolProcessing] = useState(false);
  const [pdfToolProgress, setPdfToolProgress] = useState(0);

  // Initialize diagnostics and theme
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    let interval;
    const checkInit = async () => {
      const status = await api.getInitStatus();
      setInitStatus(status);
      if (!status.initializing) {
        clearInterval(interval);
        loadDiagnostics();
      }
    };
    checkInit();
    interval = setInterval(checkInit, 2500);
    return () => clearInterval(interval);
  }, []);

  const loadDiagnostics = async () => {
    setDiagLoading(true);
    try {
      const data = await api.getStatus();
      setDiagnostics(data);
    } catch (e) {
      console.error("Failed to load backend diagnostics:", e);
    } finally {
      setDiagLoading(false);
    }
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  // Helper: Poll job status in backend
  const pollJobStatus = (jobId, onSuccess, onFailure) => {
    const interval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(jobId);
        if (job.status === 'completed') {
          clearInterval(interval);
          onSuccess(job);
        } else if (job.status === 'failed') {
          clearInterval(interval);
          onFailure(job.error || 'Operation failed');
        } else {
          // Update progress dynamically
          onProgressUpdate(jobId, job.progress);
        }
      } catch (err) {
        clearInterval(interval);
        onFailure(err.message || 'Error tracking job status');
      }
    }, 1500);
  };

  // Dynamic helper to update queue progress
  const onProgressUpdate = (jobId, progress) => {
    setConverterQueue(prev => prev.map(item => 
      item.jobId === jobId ? { ...item, progress } : item
    ));
    setCompressorQueue(prev => prev.map(item => 
      item.jobId === jobId ? { ...item, progress } : item
    ));
  };

  // =====================================================
  // TAB 1: CONVERTER HANDLERS
  // =====================================================
  const handleConverterFilesAdded = (files) => {
    const newItems = files.map(file => {
      const ext = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase();
      // Default conversion target to PDF
      return {
        id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        file,
        name: file.name,
        size: file.size,
        ext,
        targetFormat: 'pdf',
        ocr: false,
        status: 'queued',
        progress: 0,
        resultFile: null,
        errorMsg: '',
        engine: null
      };
    });
    setConverterQueue(prev => [...prev, ...newItems]);
  };

  const handleUpdateFormat = (id, targetFormat) => {
    setConverterQueue(prev => prev.map(item => 
      item.id === id ? { ...item, targetFormat } : item
    ));
  };

  const handleUpdateOcr = (id, ocr) => {
    setConverterQueue(prev => prev.map(item => 
      item.id === id ? { ...item, ocr } : item
    ));
  };

  const handleRemoveConverterItem = (id) => {
    setConverterQueue(prev => prev.filter(item => item.id !== id));
  };

  const handleConvertItem = async (id) => {
    const item = converterQueue.find(i => i.id === id);
    if (!item || item.status === 'processing') return;

    setConverterQueue(prev => prev.map(i => 
      i.id === id ? { ...i, status: 'processing', progress: 10 } : i
    ));

    try {
      const res = await api.convertFile(item.file, item.targetFormat, item.ocr);
      
      setConverterQueue(prev => prev.map(i => 
        i.id === id ? { ...i, jobId: res.job_id } : i
      ));

      pollJobStatus(
        res.job_id,
        (job) => {
          setConverterQueue(prev => prev.map(i => 
            i.id === id ? { 
              ...i, 
              status: 'completed', 
              progress: 100, 
              resultFile: job.result_file, 
              engine: job.engine 
            } : i
          ));
        },
        (error) => {
          setConverterQueue(prev => prev.map(i => 
            i.id === id ? { ...i, status: 'failed', progress: 0, errorMsg: error } : i
          ));
        }
      );
    } catch (e) {
      setConverterQueue(prev => prev.map(i => 
        i.id === id ? { ...i, status: 'failed', progress: 0, errorMsg: e.response?.data?.detail || e.message } : i
      ));
    }
  };

  const handleConvertAll = async () => {
    if (isConverterProcessing) return;
    setIsConverterProcessing(true);
    
    const pending = converterQueue.filter(i => i.status === 'queued' || i.status === 'failed');
    for (const item of pending) {
      await handleConvertItem(item.id);
    }
    
    setIsConverterProcessing(false);
  };

  const handleDownload = (id) => {
    const item = converterQueue.find(i => i.id === id);
    if (item && item.resultFile) {
      window.open(api.getDownloadUrl(item.resultFile), '_blank');
    }
  };

  const handleDownloadAllZip = () => {
    // Downloads all compiled files sequentially
    const completed = converterQueue.filter(i => i.status === 'completed' && i.resultFile);
    completed.forEach(item => {
      window.open(api.getDownloadUrl(item.resultFile), '_blank');
    });
  };

  // =====================================================
  // TAB 2: COMPRESSOR HANDLERS
  // =====================================================
  const handleCompressFilesAdded = (files) => {
    const newItems = files.map(file => {
      const ext = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase();
      return {
        id: `comp_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        file,
        name: file.name,
        size: file.size,
        ext,
        status: 'queued',
        progress: 0,
        compressedSize: null,
        resultFile: null,
        errorMsg: ''
      };
    });
    setCompressorQueue(prev => [...prev, ...newItems]);
  };

  const handleCompressItem = async (id) => {
    const item = compressorQueue.find(i => i.id === id);
    if (!item || item.status === 'processing') return;

    setCompressorQueue(prev => prev.map(i => 
      i.id === id ? { ...i, status: 'processing', progress: 10 } : i
    ));

    try {
      const quality = compressionQuality / 100;
      const res = await api.compressFile(item.file, quality);
      
      setCompressorQueue(prev => prev.map(i => 
        i.id === id ? { ...i, jobId: res.job_id } : i
      ));

      pollJobStatus(
        res.job_id,
        async (job) => {
          setCompressorQueue(prev => prev.map(i => 
            i.id === id ? { 
              ...i, 
              status: 'completed', 
              progress: 100, 
              resultFile: job.result_file,
              compressedSize: Math.round(item.size * quality) 
            } : i
          ));
        },
        (error) => {
          setCompressorQueue(prev => prev.map(i => 
            i.id === id ? { ...i, status: 'failed', progress: 0, errorMsg: error } : i
          ));
        }
      );
    } catch (e) {
      setCompressorQueue(prev => prev.map(i => 
        i.id === id ? { ...i, status: 'failed', progress: 0, errorMsg: e.response?.data?.detail || e.message } : i
      ));
    }
  };

  const handleCompressAll = async () => {
    if (isCompressorProcessing) return;
    setIsCompressorProcessing(true);
    
    const pending = compressorQueue.filter(i => i.status === 'queued' || i.status === 'failed');
    for (const item of pending) {
      await handleCompressItem(item.id);
    }
    
    setIsCompressorProcessing(false);
  };

  const handleDownloadCompressed = (id) => {
    const item = compressorQueue.find(i => i.id === id);
    if (item && item.resultFile) {
      window.open(api.getDownloadUrl(item.resultFile), '_blank');
    }
  };

  const handleRemoveCompressorItem = (id) => {
    setCompressorQueue(prev => prev.filter(item => item.id !== id));
  };

  // =====================================================
  // TAB 3: PDF EDITING TOOLS HANDLERS
  // =====================================================
  const handlePdfFilesAdded = (files) => {
    const pdfsOnly = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
    if (pdfsOnly.length === 0) {
      alert("Only PDF files are supported in this tab.");
      return;
    }
    setPdfFiles(prev => [...prev, ...pdfsOnly]);
  };

  const handleRemovePdfFile = (index) => {
    setPdfFiles(prev => prev.filter((_, idx) => idx !== index));
  };

  const runPdfTool = async () => {
    if (pdfFiles.length === 0 || isPdfToolProcessing) return;
    setIsPdfToolProcessing(true);
    setPdfToolProgress(10);
    setPdfToolResult(null);

    try {
      const formData = new FormData();
      
      if (pdfOp === 'merge') {
        const res = await api.pdfMerge(pdfFiles);
        
        setPdfToolProgress(50);
        pollJobStatus(
          res.job_id,
          (job) => {
            setPdfToolProgress(100);
            setIsPdfToolProcessing(false);
            setPdfToolResult(job.result_file);
          },
          (error) => {
            setIsPdfToolProcessing(false);
            setPdfToolProgress(0);
            alert(`Merge failed: ${error}`);
          }
        );
      } else {
        // Single file operations
        const file = pdfFiles[0];
        const options = {
          watermark_text: pdfWatermarkText,
          password: pdfPassword,
          rotation_angle: pdfRotation
        };
        const res = await api.pdfEdit(file, pdfOp, options);

        setPdfToolProgress(50);
        pollJobStatus(
          res.job_id,
          (job) => {
            setPdfToolProgress(100);
            setIsPdfToolProcessing(false);
            setPdfToolResult(job.result_file);
          },
          (error) => {
            setIsPdfToolProcessing(false);
            setPdfToolProgress(0);
            alert(`Operation failed: ${error}`);
          }
        );
      }
    } catch(e) {
      setIsPdfToolProcessing(false);
      setPdfToolProgress(0);
      alert(`Error running PDF tools: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleDownloadPdfResult = () => {
    if (pdfToolResult) {
      window.open(api.getDownloadUrl(pdfToolResult), '_blank');
    }
  };

  if (initStatus.initializing) {
    return (
      <div className="min-h-screen animated-bg flex flex-col items-center justify-center text-foreground p-4 text-center">
        <div className="glassmorphism rounded-3xl p-12 max-w-md w-full shadow-2xl flex flex-col items-center">
          <RefreshCw className="animate-spin text-primary mb-6" size={48} />
          <h2 className="text-2xl font-bold mb-3 gradient-title">Initializing Converter</h2>
          <p className="text-muted-foreground mb-6 text-sm">
            Downloading local offline engines. This is a one-time setup and may take a few minutes depending on your internet connection...
          </p>
          <div className="w-full bg-muted rounded-full h-2 mb-2 overflow-hidden">
            <div className="bg-primary h-full rounded-full animate-pulse w-full"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen animated-bg text-foreground transition-colors duration-300 antialiased font-sans overflow-hidden">
      
      {/* Animated Floating Background Shapes */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary/20 dark:bg-primary/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div className="absolute top-[20%] right-[-10%] w-72 h-72 bg-emerald-500/20 dark:bg-emerald-500/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-20%] left-[20%] w-80 h-80 bg-purple-500/20 dark:bg-purple-500/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="relative container mx-auto px-4 py-8 max-w-6xl z-10">
        
        {/* Main Header */}
        <header className="flex items-center justify-between mb-8 border-b border-border/40 pb-5 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-primary/10 text-primary animate-pulse">
              <Files size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight gradient-title">Universal Document Converter</h1>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl hover:bg-muted border border-border/60 transition-colors"
              title="Toggle Theme"
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
          </div>
        </header>

        {/* Optional Warning Removed as requested */}

        <>
            {/* Tab Controls */}
            <nav className="flex items-center border-b border-border/50 mb-8 p-1 gap-2 bg-muted/30 rounded-2xl max-w-md">
              <button
                onClick={() => setActiveTab('converter')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3.5 text-sm font-semibold rounded-xl transition-all duration-300
                  ${activeTab === 'converter' 
                    ? 'bg-card text-foreground shadow-sm' 
                    : 'text-muted-foreground hover:text-foreground'
                  }`}
              >
                <Files size={16} />
                <span>Converter</span>
              </button>
              
              <button
                onClick={() => setActiveTab('compressor')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3.5 text-sm font-semibold rounded-xl transition-all duration-300
                  ${activeTab === 'compressor' 
                    ? 'bg-card text-foreground shadow-sm' 
                    : 'text-muted-foreground hover:text-foreground'
                  }`}
              >
                <Layers size={16} />
                <span>Compressor</span>
              </button>

              <button
                onClick={() => setActiveTab('pdf-tools')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3.5 text-sm font-semibold rounded-xl transition-all duration-300
                  ${activeTab === 'pdf-tools' 
                    ? 'bg-card text-foreground shadow-sm' 
                    : 'text-muted-foreground hover:text-foreground'
                  }`}
              >
                <PenTool size={16} />
                <span>PDF Editor</span>
              </button>
            </nav>

            {/* TAB CONTENTS */}
            <main className="space-y-8">
          
          {/* TAB 1: DOCUMENT CONVERTER */}
          {activeTab === 'converter' && (
            <div className="space-y-8 animate-fadeIn">
              <DragDropZone onFilesAdded={handleConverterFilesAdded} />
              
              {converterQueue.length > 0 && (
                <ConversionQueue 
                  queue={converterQueue}
                  isProcessing={isConverterProcessing}
                  onRemove={handleRemoveConverterItem}
                  onConvert={handleConvertItem}
                  onConvertAll={handleConvertAll}
                  onDownload={handleDownload}
                  onDownloadAllZip={handleDownloadAllZip}
                  onUpdateFormat={handleUpdateFormat}
                  onUpdateOcr={handleUpdateOcr}
                />
              )}
            </div>
          )}

          {/* TAB 2: COMPRESSOR */}
          {activeTab === 'compressor' && (
            <div className="space-y-8 animate-fadeIn">
              <DragDropZone 
                onFilesAdded={handleCompressFilesAdded} 
                accept=".pdf,.jpg,.jpeg,.png,.webp"
                subtitle="Upload PDFs or images (JPG, PNG, WebP) to compress sizes"
              />

              {/* Compression Quality Setting Card */}
              <div className="glassmorphism rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="font-semibold text-sm">Target Quality / Compression Ratio:</span>
                  <span className="text-sm font-bold text-primary font-mono">{compressionQuality}%</span>
                </div>
                <input 
                  type="range" 
                  min="10" 
                  max="100" 
                  value={compressionQuality}
                  onChange={(e) => setCompressionQuality(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary" 
                />
                <div className="flex justify-between text-2xs text-muted-foreground/70 mt-2.5">
                  <span>Max Compression (Low Quality)</span>
                  <span>Recommended (60%)</span>
                  <span>Best Quality (Low Compression)</span>
                </div>
              </div>

              {compressorQueue.length > 0 && (
                <div className="glassmorphism rounded-2xl p-6">
                  <div className="flex items-center justify-between border-b border-border/40 pb-4 mb-6">
                    <div>
                      <h3 className="font-semibold text-lg">Compressor Queue</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{compressorQueue.length} files queued</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleCompressAll}
                        disabled={isCompressorProcessing || !compressorQueue.some(i => i.status === 'queued' || i.status === 'failed')}
                        className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-xl bg-primary text-primary-foreground hover:opacity-95 disabled:opacity-50"
                      >
                        <Play size={15} />
                        <span>Compress All</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {compressorQueue.map(item => {
                      const saved = item.compressedSize ? Math.round((1 - item.compressedSize / item.size) * 100) : 0;
                      return (
                        <div key={item.id} className="border border-border/60 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2.5 rounded-xl bg-muted text-primary">
                              <FileText size={20} />
                            </div>
                            <div>
                              <div className="font-medium text-sm truncate max-w-md">{item.name}</div>
                              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                                <span>Original: {formatBytes(item.size)}</span>
                                {item.compressedSize && (
                                  <>
                                    <span>•</span>
                                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">Compressed: {formatBytes(item.compressedSize)}</span>
                                    {saved > 0 && (
                                      <span className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded text-[10px] font-semibold">
                                        Saved {saved}%
                                      </span>
                                    )}
                                  </>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center justify-between md:justify-end gap-3 border-t md:border-t-0 border-border/40 pt-3 md:pt-0">
                            {item.status === 'processing' && (
                              <span className="inline-flex items-center gap-1.5 text-xs text-primary bg-primary/10 px-2.5 py-1 rounded-full font-semibold">
                                <RefreshCw size={12} className="animate-spin" />
                                <span>Compressing {item.progress}%</span>
                              </span>
                            )}
                            {item.status === 'completed' && (
                              <span className="inline-flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full font-semibold">
                                <CheckCircle2 size={12} />
                                <span>Ready</span>
                              </span>
                            )}
                            {item.status === 'failed' && (
                              <span className="inline-flex items-center gap-1.5 text-xs text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-full font-semibold">
                                <AlertCircle size={12} />
                                <span>Failed: {item.errorMsg}</span>
                              </span>
                            )}

                            <div className="flex items-center gap-1.5">
                              {item.status === 'completed' && (
                                <button
                                  onClick={() => handleDownloadCompressed(item.id)}
                                  className="p-2 rounded-xl text-emerald-600 hover:bg-emerald-500/10"
                                >
                                  <Download size={16} />
                                </button>
                              )}
                              <button
                                onClick={() => handleRemoveCompressorItem(item.id)}
                                disabled={item.status === 'processing'}
                                className="p-2 rounded-xl text-muted-foreground/60 hover:text-rose-500 hover:bg-rose-500/10"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: PDF TOOLS */}
          {activeTab === 'pdf-tools' && (
            <div className="space-y-8 animate-fadeIn">
              <DragDropZone 
                onFilesAdded={handlePdfFilesAdded}
                accept=".pdf"
                subtitle="Upload PDF files to perform merge, split, rotate, or watermark edit actions"
              />

              {/* PDF Settings Dashboard */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Operations side panel */}
                <div className="glassmorphism rounded-2xl p-6 flex flex-col gap-3">
                  <h4 className="font-semibold text-sm border-b border-border/40 pb-2 mb-2">PDF Operation</h4>
                  <button
                    onClick={() => { setPdfOp('merge'); setPdfToolResult(null); }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-semibold border text-left transition-all
                      ${pdfOp === 'merge' 
                        ? 'border-primary/30 bg-primary/5 text-primary' 
                        : 'border-border/60 text-muted-foreground hover:bg-muted/40'
                      }`}
                  >
                    <Layers size={14} />
                    <span>Merge Multiple PDFs</span>
                  </button>
                  <button
                    onClick={() => { setPdfOp('split'); setPdfToolResult(null); }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-semibold border text-left transition-all
                      ${pdfOp === 'split' 
                        ? 'border-primary/30 bg-primary/5 text-primary' 
                        : 'border-border/60 text-muted-foreground hover:bg-muted/40'
                      }`}
                  >
                    <Columns size={14} />
                    <span>Split PDF (Single Pages)</span>
                  </button>
                  <button
                    onClick={() => { setPdfOp('rotate'); setPdfToolResult(null); }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-semibold border text-left transition-all
                      ${pdfOp === 'rotate' 
                        ? 'border-primary/30 bg-primary/5 text-primary' 
                        : 'border-border/60 text-muted-foreground hover:bg-muted/40'
                      }`}
                  >
                    <RotateCw size={14} />
                    <span>Rotate Pages</span>
                  </button>
                  <button
                    onClick={() => { setPdfOp('watermark'); setPdfToolResult(null); }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-semibold border text-left transition-all
                      ${pdfOp === 'watermark' 
                        ? 'border-primary/30 bg-primary/5 text-primary' 
                        : 'border-border/60 text-muted-foreground hover:bg-muted/40'
                      }`}
                  >
                    <PenTool size={14} />
                    <span>Apply Watermark Text</span>
                  </button>
                  <button
                    onClick={() => { setPdfOp('encrypt'); setPdfToolResult(null); }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-semibold border text-left transition-all
                      ${pdfOp === 'encrypt' 
                        ? 'border-primary/30 bg-primary/5 text-primary' 
                        : 'border-border/60 text-muted-foreground hover:bg-muted/40'
                      }`}
                  >
                    <Lock size={14} />
                    <span>Encrypt with Password</span>
                  </button>
                </div>

                {/* Configurations parameters based on selected operation */}
                <div className="glassmorphism rounded-2xl p-6 md:col-span-2">
                  <h4 className="font-semibold text-sm border-b border-border/40 pb-2 mb-4">Configuration Settings</h4>
                  
                  {pdfOp === 'merge' && (
                    <div className="text-xs text-muted-foreground leading-relaxed space-y-2">
                      <p>• Renders all added PDFs in the queue combined in order.</p>
                      <p>• You can add 2 or more PDF documents to merge.</p>
                    </div>
                  )}

                  {pdfOp === 'split' && (
                    <div className="text-xs text-muted-foreground leading-relaxed space-y-2">
                      <p>• Extract each page of the uploaded PDF to a separate single-page PDF.</p>
                      <p>• Results are compiled in a single package folder on the server.</p>
                    </div>
                  )}

                  {pdfOp === 'rotate' && (
                    <div className="space-y-4">
                      <label className="text-xs font-semibold block text-muted-foreground">Select Rotation Angle:</label>
                      <select 
                        value={pdfRotation}
                        onChange={(e) => setPdfRotation(parseInt(e.target.value))}
                        className="bg-background border border-border/80 rounded-xl px-3 py-2 text-sm focus:outline-none w-full max-w-xs font-medium"
                      >
                        <option value="90">90° Clockwise</option>
                        <option value="180">180° Flip</option>
                        <option value="270">270° Counter-Clockwise</option>
                      </select>
                    </div>
                  )}

                  {pdfOp === 'watermark' && (
                    <div className="space-y-4">
                      <label className="text-xs font-semibold block text-muted-foreground">Watermark Text:</label>
                      <input 
                        type="text" 
                        value={pdfWatermarkText}
                        onChange={(e) => setPdfWatermarkText(e.target.value)}
                        placeholder="CONFIDENTIAL"
                        className="bg-background border border-border/80 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary w-full max-w-md font-medium"
                      />
                    </div>
                  )}

                  {pdfOp === 'encrypt' && (
                    <div className="space-y-4">
                      <label className="text-xs font-semibold block text-muted-foreground">Password Protection:</label>
                      <input 
                        type="password" 
                        value={pdfPassword}
                        onChange={(e) => setPdfPassword(e.target.value)}
                        placeholder="Enter password..."
                        className="bg-background border border-border/80 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary w-full max-w-md font-medium"
                      />
                    </div>
                  )}

                  {/* Actions workspace queue */}
                  {pdfFiles.length > 0 && (
                    <div className="mt-6 border-t border-border/40 pt-5">
                      <h5 className="font-semibold text-xs text-muted-foreground uppercase mb-3 tracking-wider">Queue:</h5>
                      <div className="space-y-2 mb-5">
                        {pdfFiles.map((f, i) => (
                          <div key={i} className="flex items-center justify-between bg-muted/40 border border-border/40 rounded-xl px-3 py-2">
                            <span className="text-xs font-medium truncate max-w-xs">{f.name}</span>
                            <button
                              onClick={() => handleRemovePdfFile(i)}
                              className="text-muted-foreground/60 hover:text-rose-500"
                            >
                              <Trash2 size={13} />
                            </button>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center gap-4">
                        <button
                          onClick={runPdfTool}
                          disabled={isPdfToolProcessing || (pdfOp === 'merge' && pdfFiles.length < 2)}
                          className="inline-flex items-center gap-1.5 px-4.5 py-2.5 text-sm font-semibold rounded-xl bg-primary text-primary-foreground hover:opacity-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                          {isPdfToolProcessing ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                          <span>Execute {pdfOp.toUpperCase()}</span>
                        </button>
                        
                        {isPdfToolProcessing && (
                          <span className="text-xs text-primary font-semibold">Running operation...</span>
                        )}

                        {pdfToolResult && (
                          <button
                            onClick={handleDownloadPdfResult}
                            className="inline-flex items-center gap-1.5 px-4.5 py-2.5 text-sm font-semibold rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20 transition-all border border-emerald-500/20"
                          >
                            <Download size={14} />
                            <span>Download PDF Result</span>
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </>
      </div>
    </div>
  );
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};
