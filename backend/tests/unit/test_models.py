from backend.app.models import FileMeta, FileListResponse

def test_models_examples():
    fm = FileMeta(name="x", size=1, content_type="text/plain", uploaded_at=1.0)
    fl = FileListResponse(files=[fm])
    assert fl.ok and fl.files[0].name == "x"
