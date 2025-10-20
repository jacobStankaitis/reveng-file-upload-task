from pydantic import BaseModel, Field
from typing import List

class FileMeta(BaseModel):
    """
    Metadata schema for a single uploaded file.
    """
    name: str = Field(examples=["report.pdf"])
    size: int = Field(ge=0, examples=[12345])
    content_type: str = Field(examples=["application/pdf"])
    uploaded_at: float = Field(description="epoch seconds", examples=[1734712345.12])

class UploadResponse(BaseModel):
    """
    Response schema for a successful file upload.
    """
    ok: bool = True
    file: FileMeta

class FileListResponse(BaseModel):
    """
    Response schema for listing uploaded files.
    """
    ok: bool = True
    files: List[FileMeta] = []
