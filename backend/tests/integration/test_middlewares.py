import asyncio

import httpx
import pytest
from fastapi import FastAPI

from app.metrics import Metrics
from app.middlewares import RequestContextMiddleware, request_id_var, trace_id_var


@pytest.mark.asyncio
async def test_request_context_middleware_injects_ids():
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/check")
    async def check():
        rid = request_id_var.get()
        tid = trace_id_var.get()
        return {"rid": rid, "tid": tid}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/check")
        data = r.json()
        assert r.status_code == 200
        assert len(data["rid"]) > 0
        assert len(data["tid"]) > 0
        assert r.headers["x-request-id"]
        assert r.headers["traceparent"].startswith("00-")

@pytest.mark.asyncio
async def test_in_flight_middleware_tracks_active_requests():
    metrics = Metrics()
    app = FastAPI()

    @app.middleware("http")
    async def in_flight_mw(request, call_next):
        await metrics.inc_in_progress()
        try:
            return await call_next(request)
        finally:
            await metrics.dec_in_progress()

    @app.get("/ok")
    async def ok():
        await asyncio.sleep(0.01)
        return {"ok": True}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        assert metrics.gauges.requests_in_progress == 0
        r = await ac.get("/ok")
        assert r.status_code == 200
        assert metrics.gauges.requests_in_progress == 0