import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol


@dataclass
class StoredFile:
    """
    Internal representation of a stored file in memory.
    """
    name: str
    size: int
    content_type: str
    uploaded_at: float
    data: bytes

class IFileStore(Protocol):
    """
    Protocol defining asynchronous file storage interface.
    """
    async def save(self, name: str, content_type: str, data: bytes) -> StoredFile: ...
    async def list(self) -> List[StoredFile]: ...
    async def clear(self) -> None: ...
    async def get(self, name: str) -> Optional[StoredFile]: ...

class MemoryStore(IFileStore):
    """
    Thread-safe in-memory implementation of the file store interface.
    """
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._files: Dict[str, StoredFile] = {}

    async def save(self, name: str, content_type: str, data: bytes) -> StoredFile:
        sf = StoredFile(name=name, content_type=content_type, data=data,
                        size=len(data), uploaded_at=time.time())
        async with self._lock:
            self._files[name] = sf
        return sf

    async def list(self) -> List[StoredFile]:
        async with self._lock:
            return sorted(self._files.values(), key=lambda f: f.uploaded_at, reverse=True)

    async def clear(self) -> None:
        async with self._lock:
            self._files.clear()

    async def get(self, name: str) -> Optional[StoredFile]:
        async with self._lock:
            return self._files.get(name)

class S3StubStore(IFileStore):
    """
    Stubbed file store mimicking S3 behavior using an inner MemoryStore.
    """
    def __init__(self)-> None: self._inner = MemoryStore()
    async def save(self, name: str, content_type: str, data: bytes)->StoredFile:
        return await self._inner.save(name, content_type, data)
    async def list(self)->list[StoredFile]: return await self._inner.list()
    async def get(self, name: str)->StoredFile|None: return await self._inner.get(name)
    async def clear(self)-> None: return await self._inner.clear()

def make_store(kind: str) -> IFileStore:
    """
    Factory function for creating a file store backend.
    :param kind: "memory" for MemoryStore, anything else for S3StubStore.
    :return: IFileStore implementation.
    """
    return MemoryStore() if kind == "memory" else S3StubStore()
