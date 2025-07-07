import pytest
from fastapi.testclient import TestClient
from main import app
from analyzer import analyze_audio
from schemas import AnalysisResult

client = TestClient(app)

def test_analyze_audio_success(dummy_audio_file):
    """Test the core analyze_audio function with a valid dummy file."""
    result = analyze_audio(dummy_audio_file)
    assert isinstance(result, AnalysisResult)
    assert result.tempo > 0
    assert result.key is not None
    assert len(result.segments) > 0

def test_analyze_audio_file_not_found():
    """Test analyze_audio with a non-existent file path."""
    with pytest.raises(IOError):
        analyze_audio("non_existent_file.wav")

def test_api_upload_success(dummy_audio_file):
    """Test the /analyze/ API endpoint with a successful upload."""
    with open(dummy_audio_file, "rb") as f:
        response = client.post("/analyze/", files={"file": ("test.wav", f, "audio/wav")})
    
    assert response.status_code == 200
    data = response.json()
    assert "tempo" in data
    assert "key" in data
    assert "segments" in data
    assert isinstance(data["segments"], list)

def test_api_upload_invalid_file_type():
    """Test the /analyze/ API endpoint with a non-audio file."""
    response = client.post("/analyze/", files={"file": ("test.txt", b"some text", "text/plain")})
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
