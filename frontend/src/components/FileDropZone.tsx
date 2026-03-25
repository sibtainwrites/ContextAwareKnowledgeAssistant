import { useRef, useState, type DragEvent, type ChangeEvent } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';

interface FileDropZoneProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
}

export default function FileDropZone({ onFileSelect, isUploading }: FileDropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = (file: File) => {
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      alert('Only PDF files are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10 MB. Please choose a smaller file.');
      return;
    }
    setSelectedFile(file);
    onFileSelect(file);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const onDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
  };

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onClick={() => !isUploading && inputRef.current?.click()}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      className={`
        relative flex flex-col items-center justify-center gap-3
        w-full min-h-[180px] rounded-xl border-2 border-dashed
        transition-all duration-200 cursor-pointer
        ${
          dragOver
            ? 'border-indigo-400 bg-indigo-950/30'
            : 'border-[var(--border)] bg-[var(--bg-main)] hover:border-[var(--text-secondary)]'
        }
        ${isUploading ? 'pointer-events-none opacity-60' : ''}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={onChange}
      />

      {isUploading ? (
        <>
          <Loader2 size={32} className="text-indigo-400 animate-spin" />
          <p className="text-sm text-[var(--text-secondary)]">Uploading & processing…</p>
        </>
      ) : selectedFile ? (
        <>
          <FileText size={32} className="text-indigo-400" />
          <p className="text-sm text-[var(--text-primary)] font-medium">{selectedFile.name}</p>
          <p className="text-xs text-[var(--text-secondary)]">Click or drop to replace</p>
        </>
      ) : (
        <>
          <Upload size={32} className="text-[var(--text-secondary)]" />
          <p className="text-sm text-[var(--text-secondary)]">
            Drop PDF here or <span className="text-indigo-400 underline">click to browse</span>
          </p>
          <p className="text-xs text-[var(--text-secondary)]">Max 10 MB</p>
        </>
      )}
    </div>
  );
}
