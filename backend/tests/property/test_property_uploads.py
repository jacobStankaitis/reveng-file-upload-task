# tests/property/test_property_uploads.py
import pytest
import httpx
from hypothesis import given, settings as hsettings, strategies as st
from app.main import app
from app.config import settings as cfg

@hsettings(deadline=None, max_examples=25)
@given(name=st.text(min_size=1, max_size=50))
@pytest.mark.asyncio
async def test_filename_is_valid_or_rejected(name):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"{cfg.API_PREFIX}/upload", files={"file": (name, b"ok", "text/plain")})
        # Two valid outcomes:
        #  - 200 with sanitized non-empty name (no path separators)
        #  - 400 invalid filename (if secure_filename would be empty)
        if r.status_code == 200:
            safe = r.json()["file"]["name"]
            assert isinstance(safe, str) and len(safe) > 0
            assert "/" not in safe and "\\" not in safe
        else:
            assert r.status_code == 400
            assert "invalid filename" in r.text
