import React from 'react';
import { ShieldCheck, CheckCircle2, AlertOctagon, XCircle, Cpu } from 'lucide-react';

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

  const { engines, os, python_version, corrupted } = diagnostics;

  const engineList = [
    { id: 'libreoffice', name: 'Bundled LibreOffice', desc: 'Converts Word, Excel, and Presentation office files' },
    { id: 'tesseract', name: 'Bundled Tesseract', desc: 'Translates scan images to searchable PDFs (OCR)' },
    { id: 'ghostscript', name: 'Bundled Ghostscript', desc: 'Performs vector layout and compression routines' },
    { id: 'poppler', name: 'Bundled Poppler', desc: 'Renders, parses, and extracts elements from PDF structures' },
    { id: 'imagemagick', name: 'Bundled ImageMagick', desc: 'Converts and edits legacy image patterns' },
    { id: 'pandoc', name: 'Bundled Pandoc', desc: 'Handles rich markdown and document markup translation' },
    { id: 'ffmpeg', name: 'Bundled FFmpeg', desc: 'Processes metadata streams and media packages' }
  ];

  return (
    <div className="glassmorphism rounded-2xl p-6 mb-8 transition-all duration-300">
      <div className="flex items-center justify-between mb-4 border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className={corrupted ? "text-rose-500" : "text-emerald-500"} size={20} />
          <h3 className="font-semibold text-lg">Bundled Engine Status</h3>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          <span>OS: {os}</span>
          <span>•</span>
          <span>Python: {python_version}</span>
        </div>
      </div>

      {corrupted && (
        <div className="flex items-center gap-3 bg-rose-500/10 border border-rose-500/20 text-rose-800 dark:text-rose-300 text-sm p-4 rounded-xl mb-6 font-semibold animate-pulse">
          <AlertOctagon className="shrink-0 text-rose-500" size={20} />
          <div>The application installation is corrupted. Please reinstall.</div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {engineList.map((engine) => {
          const status = engines[engine.id] || { available: false, path: null };
          
          return (
            <div 
              key={engine.id} 
              className={`flex items-start justify-between gap-3 p-3.5 rounded-xl border transition-colors
                ${status.available 
                  ? 'border-emerald-500/15 bg-emerald-500/[0.01]' 
                  : 'border-rose-500/15 bg-rose-500/[0.01]'
                }`}
            >
              <div className="min-w-0">
                <div className="font-semibold text-sm flex items-center gap-2 text-foreground/90">
                  <span>{engine.name}</span>
                </div>
                <p className="text-2xs text-muted-foreground leading-normal mt-0.5 max-w-sm">
                  {engine.desc}
                </p>
                {status.available && status.path && (
                  <div className="text-[10px] font-mono text-muted-foreground/50 truncate max-w-xs mt-1.5">
                    Location: {status.path}
                  </div>
                )}
              </div>

              <div className="shrink-0">
                {status.available ? (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 size={12} />
                    <span>Active</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400">
                    <XCircle size={12} />
                    <span>Missing</span>
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
