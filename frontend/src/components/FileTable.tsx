"use client";
import React from "react";

export default function FileTable({
  files,
}: {
  files: Array<{
    name: string;
    size: number;
    content_type: string;
    uploaded_at: number;
  }>;
}) {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE!;

  if (!files.length)
    return (
      <div className="card" aria-live="polite">
        No files yet.
      </div>
    );
  return (
    <div className="card">
      <table className="table" aria-label="Uploaded files">
        <thead>
          <tr>
            <th>Name</th>
            <th>Size</th>
            <th>Type</th>
            <th>Uploaded</th>
            <th>Download</th>
          </tr>
        </thead>
        <tbody>
          {files.map((f) => (
            <tr key={`${f.name}-${f.uploaded_at}`}>
              <td>{f.name}</td>
              <td>{(f.size / 1024).toFixed(1)} KB</td>
              <td>{f.content_type}</td>
              <td>{new Date(f.uploaded_at * 1000).toLocaleString()}</td>
              <td>
                <a
                  href={`${API_BASE}/files/${encodeURIComponent(f.name)}`}
                  download
                  aria-label={`Download ${f.name}`}
                >
                  Download
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
