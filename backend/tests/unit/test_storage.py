import pytest
from backend.app.storage import MemoryStore

@pytest.mark.asyncio
async def test_memory_store_roundtrip():
    s = MemoryStore()
    await s.save("a.txt", "text/plain", b"hi")
    files = await s.list()
    assert files[0].name == "a.txt" and files[0].size == 2
