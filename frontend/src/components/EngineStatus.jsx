import React from 'react';
import { ShieldCheck, Info, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';

export default function EngineStatus({ diagnostics, loading }) {
  if (loading) {
    return (
      <div className="glassmorphism rounded-2xl p-6 mb-8 animate-pulse">
        <div className="h-5 w-40 bg-muted-foreground/10 rounded mb-4" />
        <div className="space-y-3">
          <div className="h-4 bg-muted-foreground/10 rounded w-full" />
          <div className="h-4 bg-muted-foreground/10 rounded w-5/6" />
        </div>
      </div>
    );
  }

  if (!diagnostics || !diagnostics.engines) {
    return (
      <div className="glassmorphism rounded-2xl p-6 mb-8 text-center text-muted-foreground">
        <Cpu className="mx-auto mb-2 text-muted-foreground/40 animate-spin" />
        <p className="text-sm">Connecting to local converter daemon...</p>
      </div>
    );
  }

  const { engines, os, python_version } = diagnostics;

  const engineList = [
    {
      id: 'libreoffice',
      name: 'LibreOffice Headless Engine',
      description: 'Needed for high-fidelity conversion of DOC, DOCX, XLSX, ODS, PPTX, ODP.',
      status: engines.libreoffice || { available: false, path: null },
      installGuide: 'Download and install LibreOffice on your computer. Make sure it is added to your environment variables PATH, or installed in its default directory.'
    },
    {
      id: 'tesseract',
      name: 'Tesseract OCR Text Recognition',
      description: 'Needed to extract text from images and compile searchable PDFs.',
      status: engines.tesseract || { available: false, path: null },
      installGuide: 'Install Tesseract OCR on your computer (e.g. via brew on macOS, apt on Linux, or installer on Windows) and add it to your PATH.'
    },
    {
      id: 'pymupdf',
      name: 'PyMuPDF (fitz) Engine',
      description: 'Used for PDF rendering, page manipulation, text extraction, splitting, and merging.',
      status: engines.pymupdf || { available: true, path: 'Native Python Package' }
    },
    {
      id: 'pillow',
      name: 'Pillow Graphics Processing',
      description: 'Used for cropping, rotating, scaling, and compressing JPG/PNG/WEBP image assets.',
      status: engines.pillow || { available: true, path: 'Native Python Package' }
    }
  ];

  const anyMissing = engineList.some(e => !e.status.available);

  return (
    <div className="glassmorphism rounded-2xl p-6 mb-8 transition-all duration-300">
      <div className="flex items-center justify-between mb-4 border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-emerald-500" size={20} />
          <h3 className="font-semibold text-lg">System Health & Engines</h3>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          <span>OS: {os}</span>
          <span>•</span>
          <span>Python: {python_version}</span>
        </div>
      </div>

      {anyMissing && (
        <div className="flex gap-2.5 bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 text-xs p-3.5 rounded-xl mb-4 leading-relaxed">
          <AlertTriangle className="shrink-0 text-amber-500" size={16} />
          <div>
            <strong>Missing engines detected!</strong> The application will run, but will fall back to basic Python libraries for Word/Excel/PowerPoint formats. High-fidelity layouts and OCR functionality will be restricted.
          </div>
        </div>
      )}

      <div className="space-y-4">
        {engineList.map((engine) => (
          <div key={engine.id} className="group relative flex items-start justify-between gap-4 p-2.5 rounded-xl hover:bg-muted/40 transition-colors">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-sm text-foreground/90">{engine.name}</span>
                {engine.installGuide && (
                  <div className="relative inline-block cursor-help">
                    <Info size={13} className="text-muted-foreground/60 hover:text-primary transition-colors" />
                    <div className="absolute left-0 bottom-6 hidden group-hover:block w-72 p-3 bg-slate-900 text-slate-100 dark:bg-slate-800 text-xs rounded-xl shadow-xl z-20 leading-relaxed border border-slate-700">
                      {engine.installGuide}
                    </div>
                  </div>
                )}
              </div>
              <p className="text-xs text-muted-foreground leading-normal max-w-md">
                {engine.description}
              </p>
              {engine.status.path && (
                <div className="text-[10px] font-mono text-muted-foreground/60 truncate max-w-sm mt-1">
                  Path: {engine.status.path}
                </div>
              )}
            </div>

            <div className="shrink-0">
              {engine.status.available ? (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 size={12} />
                  <span>Ready</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400">
                  <AlertTriangle size={12} />
                  <span>Fallback</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
