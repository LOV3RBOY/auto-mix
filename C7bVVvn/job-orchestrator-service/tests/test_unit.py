import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, JOB_STATUS, update_job_status
import httpx

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_job_status():
    """Fixture to clear the in-memory job store before each test."""
    JOB_STATUS.clear()

def test_create_track_endpoint(mocker):
    """Test the /create-track endpoint."""
    # Mock the Celery chain and apply_async call
    mock_apply_async = MagicMock()
    mock_chain = MagicMock()
    mock_chain.apply_async.return_value = mock_apply_async
    mocker.patch('celery.chain', return_value=mock_chain)

    response = client.post("/create-track", json={"prompt": "test prompt"})
    
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    
    job_id = data["job_id"]
    assert job_id in JOB_STATUS
    assert JOB_STATUS[job_id]["status"] == "PENDING"
    
    mock_chain.apply_async.assert_called_once()

def test_get_job_status_endpoint():
    """Test the /jobs/{job_id} endpoint."""
    job_id = "test-job-123"
    JOB_STATUS[job_id] = {"status": "SUCCESS", "result": {"url": "test.wav"}}
    
    response = client.get(f"/jobs/{job_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "SUCCESS"
    assert data["result"]["url"] == "test.wav"

def test_get_job_status_not_found():
    """Test getting status for a non-existent job."""
    response = client.get("/jobs/non-existent-job")
    assert response.status_code == 404

@patch('main.settings')
@patch('httpx.Client')
def test_run_prompt_parser_task(MockClient, mock_settings):
    """Test the prompt parser Celery task."""
    from main import run_prompt_parser
    
    mock_settings.PROMPT_PARSER_URL = "http://fake-url/parse"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "C Minor"}
    
    mock_client_instance = MockClient.return_value.__enter__.return_value
    mock_client_instance.post.return_value = mock_response

    # We call the task directly, not through Celery
    result = run_prompt_parser("job-1", "a prompt")
    
    assert result == {"key": "C Minor"}
    mock_client_instance.post.assert_called_once_with(
        "http://fake-url/parse", json={"prompt": "a prompt"}, timeout=30
    )

@patch('main.settings')
@patch('httpx.Client')
def test_task_retry_on_http_error(MockClient, mock_settings):
    """Test that a task retries on HTTP request error."""
    from main import run_sound_generation
    
    mock_settings.SOUND_GENERATION_URL = "http://fake-url/gen"
    mock_client_instance = MockClient.return_value.__enter__.return_value
    mock_client_instance.post.side_effect = httpx.RequestError("Connection failed")
    
    # Mock the task's `retry` method
    mock_task = MagicMock()
    mock_task.retry.side_effect = Exception("Retry called")

    with pytest.raises(Exception, match="Retry called"):
        run_sound_generation.apply(
            (mock_task,),
            ({"prompt_spec": {}}, "job-1")
        ).get()
