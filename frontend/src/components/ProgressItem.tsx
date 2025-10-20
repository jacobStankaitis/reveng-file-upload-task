"use client";
import React from "react";

export default function ProgressItem({
  fileName,
  progress,
  onCancel,
}: {
  fileName: string;
  progress: number;
  onCancel: () => void;
}) {
  return (
    <div className="card" aria-live="polite">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <strong>{fileName}</strong>
        <button onClick={onCancel} aria-label={`Cancel upload for ${fileName}`}>
          Cancel
        </button>
      </div>
      <div className="progress">
        <div style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
