import React, { useRef, useState } from 'react';
import { Upload, FileText, Sparkles } from 'lucide-react';

export default function DragDropZone({ onFilesAdded, accept = "*", subtitle }) {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFilesAdded(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFilesAdded(Array.from(e.target.files));
      // Reset input value to allow selecting the same file again
      e.target.value = '';
    }
  };

  const triggerBrowse = () => {
    fileInputRef.current?.click();
  };

  const formats = [
    { name: 'Word', ext: '.docx, .doc, .odt', color: 'bg-blue-500/10 text-blue-600 dark:text-blue-400' },
    { name: 'Excel', ext: '.xlsx, .xls, .csv, .ods', color: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' },
    { name: 'Notebooks', ext: '.ipynb', color: 'bg-amber-500/10 text-amber-600 dark:text-amber-400' },
    { name: 'Images', ext: '.png, .jpg, .webp, .heic', color: 'bg-pink-500/10 text-pink-600 dark:text-pink-400' },
    { name: 'Presentations', ext: '.pptx, .ppt, .odp', color: 'bg-red-500/10 text-red-600 dark:text-red-400' },
    { name: 'Code & Text', ext: '.py, .js, .md, .txt, .json', color: 'bg-purple-500/10 text-purple-600 dark:text-purple-400' },
  ];

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={triggerBrowse}
      className={`relative w-full overflow-hidden transition-all duration-300 ease-out border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer group text-center
        ${isDragOver 
          ? 'border-primary bg-primary/5 scale-[0.99] shadow-inner shadow-primary/10' 
          : 'border-muted-foreground/30 bg-card hover:border-primary/60 hover:shadow-lg hover:shadow-primary/5 hover:scale-[1.01]'
        }`}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={accept}
        multiple
        className="hidden"
      />

      <div className={`p-4 rounded-full mb-4 transition-transform duration-500 ease-out group-hover:scale-110 group-hover:rotate-6
        ${isDragOver ? 'bg-primary/20 text-primary animate-bounce' : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary'}`}>
        <Upload size={32} />
      </div>

      <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
        Drag and drop files here
      </h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-sm">
        {subtitle || "Select folders or multiple files directly from your desktop to begin local processing"}
      </p>

      {/* Supported format badges */}
      <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
        {formats.map((f, i) => (
          <div key={i} className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border border-transparent transition-all duration-300 hover:border-current ${f.color}`}>
            <FileText size={12} />
            <span>{f.name}</span>
            <span className="opacity-60">({f.ext})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
