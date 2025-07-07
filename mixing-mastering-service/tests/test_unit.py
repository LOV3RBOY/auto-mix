import pytest
from unittest.mock import patch, MagicMock
from dsp_pipeline import process_mixing_job
from schemas import MixingRequest
import pedalboard

@pytest.fixture
def mock_fs(mocker):
    """Mocks filesystem-related functions."""
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.makedirs')
    mocker.patch('pedalboard.io.write')

def test_process_mixing_job_success(mock_fs):
    """Test a successful mixing job processing run."""
    stem_paths = [
        "/stems/job1_drums.wav",
        "/stems/job1_bass.wav",
        "/stems/job1_synth.wav"
    ]
    request = MixingRequest(stem_paths=stem_paths)
    
    output_path = process_mixing_job(request)
    
    assert output_path.startswith("/stems/mastered_mix_")
    assert output_path.endswith(".wav")
    
    # Verify pedalboard.io.write was called
    pedalboard.io.write.assert_called_once()


def test_process_mixing_job_creates_dir(mocker):
    """Test that the output directory is created if it doesn't exist."""
    mocker.patch('os.path.exists', return_value=False)
    mock_makedirs = mocker.patch('os.makedirs')
    mocker.patch('pedalboard.io.write')

    request = MixingRequest(stem_paths=["/stems/new_dir/test.wav"])
    process_mixing_job(request)
    
    mock_makedirs.assert_called_once_with("/stems/new_dir")

def test_dsp_pipeline_instantiation(mocker):
    """Verify that the Pedalboard is created with the expected effects."""
    mock_pedalboard = MagicMock()
    mocker.patch('pedalboard.Pedalboard', return_value=mock_pedalboard)
    mocker.patch('pedalboard.io.write')
    mocker.patch('os.path.exists', return_value=True)
    
    request = MixingRequest(stem_paths=["/stems/test.wav"])
    process_mixing_job(request)
    
    # Check that Pedalboard was initialized twice (once for processing, once for mastering)
    assert pedalboard.Pedalboard.call_count >= 2
