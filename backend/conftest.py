import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import store  # noqa: E402


@pytest.fixture(autouse=True)
async def clear_store_between_tests():
    await store.clear()
    yield
    await store.clear()