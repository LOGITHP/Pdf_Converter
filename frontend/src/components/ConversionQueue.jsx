import React from 'react';
import { 
  FileText, Trash2, Download, Play, 
  CheckCircle2, XCircle, RefreshCw, Archive, Sparkles
} from 'lucide-react';

export default function ConversionQueue({ 
  queue, 
  isProcessing, 
  onRemove, 
  onConvert, 
  onConvertAll, 
  onDownload, 
  onDownloadAllZip,
  onUpdateFormat,
  onUpdateOcr
}) {
  const getFileIconColor = (ext) => {
    const extColors = {
      pdf: 'text-red-500',
      docx: 'text-blue-500', doc: 'text-blue-500', odt: 'text-blue-500',
      xlsx: 'text-emerald-500', xls: 'text-emerald-500', csv: 'text-emerald-500', ods: 'text-emerald-500',
      pptx: 'text-rose-500', ppt: 'text-rose-500', odp: 'text-rose-500',
      ipynb: 'text-amber-600',
      png: 'text-pink-500', jpg: 'text-pink-500', jpeg: 'text-pink-500', webp: 'text-pink-500', heic: 'text-pink-500',
      py: 'text-violet-500', js: 'text-violet-500', html: 'text-violet-500', css: 'text-violet-500',
      md: 'text-slate-800 dark:text-slate-100', txt: 'text-gray-500'
    };
    return extColors[ext.toLowerCase()] || 'text-gray-400';
  };

  const getFormatOptions = (ext) => {
    const e = ext.toLowerCase();
    if (['docx', 'doc', 'odt'].includes(e)) {
      return [
        { val: 'pdf', name: 'PDF Document (.pdf)' },
        { val: 'html', name: 'Web HTML Page (.html)' },
        { val: 'txt', name: 'Plain Text (.txt)' }
      ];
    }
    if (['xlsx', 'xls', 'ods', 'csv'].includes(e)) {
      return [
        { val: 'pdf', name: 'PDF Document (.pdf)' },
        { val: 'csv', name: 'Comma Separated CSV (.csv)' },
        { val: 'xlsx', name: 'Excel Workbook (.xlsx)' }
      ];
    }
    if (['pptx', 'ppt', 'odp'].includes(e)) {
      return [
        { val: 'pdf', name: 'PDF Document (.pdf)' },
        { val: 'png', name: 'Slide Image (.png)' }
      ];
    }
    if (e === 'ipynb') {
      return [
        { val: 'pdf', name: 'PDF Document (.pdf)' },
        { val: 'html', name: 'HTML Webpage (.html)' },
        { val: 'md', name: 'Markdown Source (.md)' },
        { val: 'py', name: 'Python Script (.py)' }
      ];
    }
    if (['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif', 'heic'].includes(e)) {
      return [
        { val: 'pdf', name: 'PDF Document (.pdf)' },
        { val: 'png', name: 'PNG Image (.png)' },
        { val: 'jpg', name: 'JPEG Image (.jpg)' },
        { val: 'webp', name: 'WebP Image (.webp)' },
        { val: 'ico', name: 'Favicon Icon (.ico)' }
      ];
    }
    // Default code / text
    if (['py', 'js', 'json', 'css', 'html', 'cpp', 'java', 'go', 'rs', 'cs', 'sh', 'yaml', 'yml', 'xml', 'md', 'txt', 'log'].includes(e)) {
      return [
        { val: 'pdf', name: 'PDF (Highlighted) (.pdf)' },
        { val: 'html', name: 'HTML Highlighted (.html)' },
        { val: 'txt', name: 'Plain Text (.txt)' }
      ];
    }
    return [{ val: 'pdf', name: 'PDF Document (.pdf)' }];
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const hasCompletedJobs = queue.some(item => item.status === 'completed' && item.resultFile);
  const hasPendingJobs = queue.some(item => item.status === 'queued' || item.status === 'failed');

  return (
    <div className="glassmorphism rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-border/40 pb-4 mb-6">
        <div>
          <h3 className="font-semibold text-lg">Conversion Queue</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {queue.length} {queue.length === 1 ? 'file' : 'files'} in workspace
          </p>
        </div>

        <div className="flex flex-wrap gap-2 w-full sm:w-auto">
          <button
            onClick={onConvertAll}
            disabled={isProcessing || !hasPendingJobs}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-xl bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-primary/10"
          >
            <Play size={15} />
            <span>Convert All</span>
          </button>
          <button
            onClick={onDownloadAllZip}
            disabled={isProcessing || !hasCompletedJobs}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-xl bg-secondary text-secondary-foreground hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Archive size={15} />
            <span>Download ZIP</span>
          </button>
        </div>
      </div>

      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
        {queue.map((item) => {
          const formats = getFormatOptions(item.ext);
          const isPdfTarget = item.targetFormat === 'pdf';
          const canOcr = isPdfTarget && ['pdf', 'png', 'jpg', 'jpeg', 'webp', 'tiff', 'bmp'].includes(item.ext.toLowerCase());

          return (
            <div
              key={item.id}
              className={`relative border rounded-2xl p-4.5 transition-all duration-300 bg-card/40 flex flex-col md:flex-row md:items-center justify-between gap-4 group/item
                ${item.status === 'completed' ? 'border-emerald-500/20 bg-emerald-500/[0.01]' : ''}
                ${item.status === 'failed' ? 'border-rose-500/20 bg-rose-500/[0.01]' : ''}
                ${item.status === 'processing' ? 'border-primary/20 bg-primary/[0.01] shadow-inner shadow-primary/[0.02]' : 'border-border/60'}
              `}
            >
              <div className="flex items-start gap-3.5 flex-1 min-w-0">
                <div className={`p-2.5 rounded-xl bg-muted shrink-0 ${getFileIconColor(item.ext)}`}>
                  <FileText size={22} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate pr-4 text-foreground/90" title={item.name}>
                    {item.name}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground mt-1">
                    <span className="font-semibold bg-muted px-2 py-0.5 rounded text-[10px] uppercase">
                      {item.ext}
                    </span>
                    <span>•</span>
                    <span>{formatBytes(item.size)}</span>
                    {item.engine && (
                      <>
                        <span>•</span>
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded font-mono">
                          Engine: {item.engine}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Middle Configuration Options */}
              <div className="flex flex-wrap items-center gap-4 shrink-0">
                {/* Format selection dropdown */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                    Convert To:
                  </label>
                  <select
                    value={item.targetFormat}
                    onChange={(e) => onUpdateFormat(item.id, e.target.value)}
                    disabled={item.status === 'processing' || item.status === 'completed'}
                    className="bg-background border border-border/80 rounded-xl px-3 py-1.5 text-xs focus:ring-1 focus:ring-primary focus:outline-none disabled:opacity-60 font-medium"
                  >
                    {formats.map((f) => (
                      <option key={f.val} value={f.val}>
                        {f.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* OCR text recognition checkbox */}
                {canOcr && (
                  <div className="flex items-center gap-2 mt-4 md:mt-0 bg-muted/40 hover:bg-muted/80 transition-colors border border-border/40 px-3 py-1.5 rounded-xl cursor-pointer">
                    <input
                      type="checkbox"
                      id={`ocr-${item.id}`}
                      checked={item.ocr}
                      onChange={(e) => onUpdateOcr(item.id, e.target.checked)}
                      disabled={item.status === 'processing' || item.status === 'completed'}
                      className="rounded border-border text-primary focus:ring-primary/20 h-4 w-4 shrink-0"
                    />
                    <label htmlFor={`ocr-${item.id}`} className="text-xs font-semibold select-none flex items-center gap-1 cursor-pointer">
                      <Sparkles size={11} className="text-primary animate-pulse" />
                      <span>Searchable (OCR)</span>
                    </label>
                  </div>
                )}
              </div>

              {/* Status and Actions */}
              <div className="flex items-center justify-between md:justify-end gap-3 border-t md:border-t-0 border-border/40 pt-3 md:pt-0 shrink-0">
                <div className="text-right flex flex-col items-start md:items-end">
                  {item.status === 'queued' && (
                    <span className="text-xs font-medium text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
                      Ready to Convert
                    </span>
                  )}
                  {item.status === 'processing' && (
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-primary bg-primary/10 px-2.5 py-1 rounded-full">
                      <RefreshCw size={12} className="animate-spin" />
                      <span>Converting {item.progress}%</span>
                    </span>
                  )}
                  {item.status === 'completed' && (
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full">
                      <CheckCircle2 size={12} />
                      <span>Ready</span>
                    </span>
                  )}
                  {item.status === 'failed' && (
                    <span 
                      className="group relative flex items-center gap-1.5 text-xs font-semibold text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-full cursor-help"
                      title={item.errorMsg}
                    >
                      <XCircle size={12} />
                      <span>Failed</span>
                      <div className="absolute right-0 bottom-6 hidden group-hover:block w-64 p-2 bg-slate-900 text-slate-100 text-2xs rounded shadow-lg z-20">
                        {item.errorMsg}
                      </div>
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  {item.status === 'completed' && (
                    <button
                      onClick={() => onDownload(item.id)}
                      className="p-2 rounded-xl text-emerald-600 hover:bg-emerald-500/10 transition-colors"
                      title="Download file"
                    >
                      <Download size={16} />
                    </button>
                  )}
                  
                  {item.status === 'queued' && (
                    <button
                      onClick={() => onConvert(item.id)}
                      className="p-2 rounded-xl text-primary hover:bg-primary/10 transition-colors"
                      title="Convert file"
                    >
                      <Play size={16} />
                    </button>
                  )}

                  <button
                    onClick={() => onRemove(item.id)}
                    disabled={item.status === 'processing'}
                    className="p-2 rounded-xl text-muted-foreground/60 hover:text-rose-500 hover:bg-rose-500/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    title="Remove item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Progress Slider Bar */}
              {item.status === 'processing' && (
                <div className="absolute bottom-0 left-0 h-0.5 bg-primary/20 w-full overflow-hidden rounded-b-2xl">
                  <div 
                    className="h-full bg-primary transition-all duration-300 ease-out" 
                    style={{ width: `${item.progress}%` }} 
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
