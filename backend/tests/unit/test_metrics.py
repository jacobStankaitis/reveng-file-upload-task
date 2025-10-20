
import pytest

from app.metrics import Metrics


@pytest.mark.asyncio
async def test_metrics_counters_and_gauges():
    m = Metrics()
    assert m.counters.uploads_total == 0

    await m.inc_uploads(100)
    await m.inc_in_progress()
    await m.set_queue_len(5)
    await m.dec_in_progress()

    assert m.counters.uploads_total == 1
    assert m.counters.upload_bytes_sum == 100
    assert m.gauges.requests_in_progress == 0
    assert m.gauges.queue_len == 5
    assert isinstance(m.uptime_s(), float)
    assert m.uptime_s() >= 0
