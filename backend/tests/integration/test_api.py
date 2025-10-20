import asyncio

import pytest
import httpx

from app.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_upload_and_list():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        f = {"file": ("hello.txt", b"hello", "text/plain")}
        r = await ac.post(f"{settings.API_PREFIX}/upload", files=f)
        assert r.status_code == 200
        assert r.headers["x-api-version"]
        data = r.json()
        assert data["ok"] and data["file"]["name"] == "hello.txt"

        r2 = await ac.get(f"{settings.API_PREFIX}/files")
        assert r2.status_code == 200
        assert any(x["name"] == "hello.txt" for x in r2.json()["files"])

@pytest.mark.asyncio
async def test_upload_and_list_order():
    from app.main import store

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get(f"{settings.API_PREFIX}/health")
        assert r.status_code == 200

        for name in ["a.txt", "b.txt"]:
            r = await ac.post(f"{settings.API_PREFIX}/upload",
                              files={"file": (name, b"x", "text/plain")})
            assert r.status_code == 200

        r = await ac.get(f"{settings.API_PREFIX}/files")
        names = [f["name"] for f in r.json()["files"]]
        # newest first (b.txt uploaded after a.txt)
        assert names[:2] == ["b.txt", "a.txt"]


@pytest.mark.asyncio
async def test_upload_too_large():
    transport = httpx.ASGITransport(app=app)
    huge = b"x" * (settings.MAX_UPLOAD_SIZE_BYTES + 1)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"{settings.API_PREFIX}/upload",
                          files={"file": ("big.bin", huge, "application/octet-stream")})
        assert r.status_code == 413
        assert "file too large" in r.text

@pytest.mark.asyncio
async def test_upload_timeout(monkeypatch):
    import asyncio

    async def fake_wait_for(*a, **k):
        raise asyncio.TimeoutError

    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"{settings.API_PREFIX}/upload",
                          files={"file": ("slow.txt", b"x", "text/plain")})
        assert r.status_code == 408

@pytest.mark.asyncio
async def test_concurrent_uploads_and_listing():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        async def up(i):
            data = {"file": (f"f{i}.txt", f"data{i}".encode(), "text/plain")}
            resp = await ac.post(f"{settings.API_PREFIX}/upload", files=data)
            assert resp.status_code == 200
            return resp.json()["file"]["name"]

        results = await asyncio.gather(*[up(i) for i in range(10)])
        assert len(set(results)) == 10

        r = await ac.get(f"{settings.API_PREFIX}/files")
        names = [f["name"] for f in r.json()["files"]]
        for nm in results:
            assert nm in names
@pytest.mark.asyncio
async def test_filename_sanitization():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        f = {"file": ("../../etc/passwd", b"bad", "text/plain")}
        r = await ac.post(f"{settings.API_PREFIX}/upload", files=f)
        data = r.json()
        assert "/" not in data["file"]["name"]
        assert "\\" not in data["file"]["name"]
        assert data["file"]["name"].endswith(".passwd") or "passwd" in data["file"]["name"]