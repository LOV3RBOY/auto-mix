import pytest
import numpy as np
import soundfile as sf
import tempfile
import os

@pytest.fixture(scope="module")
def dummy_audio_file():
    """Creates a temporary dummy WAV file for testing."""
    sample_rate = 22050
    duration = 5  # seconds
    frequency = 440  # A4
    
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    amplitude = np.iinfo(np.int16).max * 0.5
    data = amplitude * np.sin(2. * np.pi * frequency * t)
    
    # Create a temporary file
    temp_f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    
    sf.write(temp_f.name, data.astype(np.int16), sample_rate)
    
    temp_f.close() # Close the file handle so other processes can access it
    
    yield temp_f.name # Provide the path to the test
    
    os.remove(temp_f.name) # Cleanup after the test session
