import pytest
from unittest.mock import patch, MagicMock
from client import create_job, poll_job_status, main

# Test create_job function
def test_create_job_success(mocker):
    """Test successful job creation."""
    mock_post = mocker.patch('requests.post')
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {"job_id": "test-job-123"}
    mock_post.return_value = mock_response

    job_id = create_job("test prompt")
    
    assert job_id == "test-job-123"
    mock_post.assert_called_once()
    assert mock_post.call_args[1]['json'] == {"prompt": "test prompt"}

def test_create_job_api_error(mocker, capsys):
    """Test API returning an error during job creation."""
    mock_post = mocker.patch('requests.post')
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
    mock_post.return_value = mock_response

    with pytest.raises(SystemExit):
        create_job("test prompt")
    
    captured = capsys.readouterr()
    assert "ERROR: Could not connect to the orchestrator service" in captured.err

# Test poll_job_status function
def test_poll_job_status_success(mocker):
    """Test polling for a job that succeeds."""
    mock_get = mocker.patch('requests.get')
    
    # Simulate responses: PENDING -> SUCCESS
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: {"status": "PENDING", "result": None}),
        MagicMock(status_code=200, json=lambda: {"status": "SUCCESS", "result": {"final_track_url": "/path/to/track.wav"}})
    ]
    
    mocker.patch('time.sleep') # Prevent actual sleeping
    
    # We don't need to check the return, just that it completes without error
    poll_job_status("test-job-123")
    assert mock_get.call_count == 2

def test_poll_job_status_failure(mocker, capsys):
    """Test polling for a job that fails."""
    mock_get = mocker.patch('requests.get')
    
    # Simulate responses: PENDING -> FAILURE
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: {"status": "PENDING", "result": None}),
        MagicMock(status_code=200, json=lambda: {"status": "FAILURE", "result": {"error": "Something went wrong"}})
    ]
    
    mocker.patch('time.sleep') # Prevent actual sleeping
    
    with pytest.raises(SystemExit):
        poll_job_status("test-job-123")
    
    captured = capsys.readouterr()
    assert "ERROR: Job failed. Reason: Something went wrong" in captured.err
    assert mock_get.call_count == 2

# Test main function with arguments
def test_main_create_command(mocker):
    """Test the main function with 'create' command."""
    mocker.patch('sys.argv', ['client.py', 'create', '--prompt', 'my awesome track'])
    mock_create_job = mocker.patch('client.create_job', return_value="job-id-456")
    mock_poll_job = mocker.patch('client.poll_job_status')

    main()

    mock_create_job.assert_called_once_with('my awesome track')
    mock_poll_job.assert_called_once_with('job-id-456')
