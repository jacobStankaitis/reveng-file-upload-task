"use client";
import React from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import UploadDropzone from "../components/UploadDropzone";
import ProgressItem from "../components/ProgressItem";
import FileTable from "../components/FileTable";
import { listFiles, uploadFile } from "../apiClient";

export default function Page() {
  const qc = useQueryClient();
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["files"],
    queryFn: () => listFiles(),
  });

  const [inFlight, setInFlight] = React.useState<
    Array<{ name: string; progress: number; abort: AbortController }>
  >([]);

  async function doUpload(files: File[]) {
    for (const f of files) {
      const abort = new AbortController();
      setInFlight((x) => [...x, { name: f.name, progress: 0, abort }]);
      try {
        await uploadFile(f, undefined, abort.signal);
        await qc.invalidateQueries({ queryKey: ["files"] });
      } catch (e) {
        console.error(e);
        alert(`Upload failed: ${f.name}`);
      } finally {
        setInFlight((x) => x.filter((i) => i.name !== f.name));
      }
    }
  }

  return (
    <div className="grid">
      <UploadDropzone onFiles={doUpload} busy={inFlight.length > 0} />
      {inFlight.map((item) => (
        <ProgressItem
          key={item.name}
          fileName={item.name}
          progress={item.progress}
          onCancel={() => {
            item.abort.abort();
            setInFlight((x) => x.filter((i) => i.name !== item.name));
          }}
        />
      ))}
      {isLoading ? (
        <div className="card">Loading…</div>
      ) : (
        <FileTable files={data?.files || []} />
      )}
      <div>
        <button onClick={() => refetch()}>Refresh</button>
      </div>
    </div>
  );
}
