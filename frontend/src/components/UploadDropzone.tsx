"use client";
import React from "react";

type Props = { onFiles: (files: File[]) => void; busy?: boolean };

export default function UploadDropzone({ onFiles, busy }: Props) {
  const [hover, setHover] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Upload files"
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          inputRef.current?.click();
        }
      }}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setHover(true);
      }}
      onDragLeave={() => setHover(false)}
      onDrop={(e) => {
        e.preventDefault();
        setHover(false);
        const files = Array.from(e.dataTransfer.files || []);
        if (files.length) onFiles(files);
      }}
      style={{
        border: "2px dashed #374151",
        padding: 24,
        borderRadius: 8,
        background: hover ? "rgba(96,165,250,0.1)" : "transparent",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        style={{ display: "none" }}
        onChange={(e) => onFiles(Array.from(e.target.files || []))}
      />
      <div style={{ textAlign: "center", color: "var(--muted)" }}>
        {busy ? "Uploading..." : "Drag & Drop files here, or click to select"}
      </div>
    </div>
  );
}
