import pytest, httpx
from fastapi import FastAPI
from app.exceptions import json_exception_handler

@pytest.mark.asyncio
async def test_json_exception_handler_returns_500(monkeypatch):
    called = {}
    def fake_error(msg, exc_info=None, extra=None):
        called.update({"msg": msg, "extra": extra})
    monkeypatch.setattr("app.exceptions.logger.error", fake_error)

    app = FastAPI(debug=False)
    app.add_exception_handler(Exception, json_exception_handler)

    @app.get("/err")
    async def err():
        raise RuntimeError("boom")

    # ↓ This is the key change
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/err")
        assert resp.status_code == 500
        assert resp.json() == {"ok": False, "error": "internal_error"}
        assert called["msg"] == "unhandled"
        assert "path" in called["extra"]
