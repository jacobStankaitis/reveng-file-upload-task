const API_BASE = process.env.NEXT_PUBLIC_API_BASE!;

export async function listFiles(signal?: AbortSignal) {
  const r = await fetch(`${API_BASE}/files`, {
    method: 'GET',
    headers: { 'x-request-id': crypto.randomUUID().replace(/-/g, '') },
    signal
  });
  if (!r.ok) throw new Error(`List failed: ${r.status}`);
  return (await r.json()) as { ok: boolean; files: Array<{name:string; size:number; content_type:string; uploaded_at:number}> };
}

export async function uploadFile(file: File, onProgress?: (pct:number)=>void, signal?: AbortSignal) {
  const fd = new FormData();
  fd.set('file', file, file.name);
  const r = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: fd,
    headers: {
      'x-request-id': crypto.randomUUID().replace(/-/g, ''),
      'x-csrf-token': 'dev'
    },
    signal
  });
  if (!r.ok) throw new Error(`Upload failed: ${r.status}`);
  return (await r.json()) as { ok: boolean; file: {name:string; size:number; content_type:string; uploaded_at:number} };
}
