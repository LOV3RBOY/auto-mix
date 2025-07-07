import numpy as np
import time
import os
from pedalboard import (
    Pedalboard,
    Compressor,
    HighpassFilter,
    Limiter,
    Loudness,
    Gain,
    EQ
)
from pedalboard.io import write

from schemas import MixingRequest

SAMPLE_RATE = 48000
TARGET_LOUDNESS_LUFS = -14.0
MOCK_STEM_DURATION_SECONDS = 10 

def _create_mock_audio(num_channels: int, duration_seconds: int, sample_rate: int) -> np.ndarray:
    num_samples = int(duration_seconds * sample_rate)
    return np.zeros((num_channels, num_samples), dtype=np.float32)

def process_mixing_job(request: MixingRequest) -> str:
    stems = []
    for _ in request.stem_paths:
        # In this mock version, we generate silent audio instead of reading files.
        # A real implementation would use:
        # from pedalboard.io import read
        # audio, _ = read(stem_path)
        # stems.append(audio)
        stems.append(_create_mock_audio(2, MOCK_STEM_DURATION_SECONDS, SAMPLE_RATE))
    
    # Mix all stems together by summing them.
    mix = np.zeros_like(stems[0])
    for stem in stems:
        mix += stem

    # Normalize the mix to avoid clipping before processing if it has content
    if np.any(mix):
        mix /= np.max(np.abs(mix))

    # Create a Pedalboard with a chain of effects.
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=35.0),
        Compressor(threshold_db=-18, ratio=3, attack_ms=5, release_ms=150),
        EQ(low_shelf_db=1.5, low_shelf_frequency_hz=100,
           high_shelf_db=1.0, high_shelf_frequency_hz=10000),
    ], sample_rate=SAMPLE_RATE)
    
    processed_mix = board(mix)
    
    # Measure the loudness of the processed mix.
    meter = Loudness(block_size=0.400)
    loudness_lufs = meter(processed_mix)
    
    # Calculate the gain needed to reach the target loudness.
    gain_db = TARGET_LOUDNESS_LUFS - loudness_lufs
    
    # Create a final mastering board with gain and a limiter.
    mastering_board = Pedalboard([
        Gain(gain_db=gain_db),
        Limiter(threshold_db=-1.0, release_ms=50.0)
    ], sample_rate=SAMPLE_RATE)
    
    mastered_mix = mastering_board(processed_mix)

    # Ensure the output directory exists. The path comes from the shared volume.
    output_dir = os.path.dirname(request.stem_paths[0])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = int(time.time())
    output_filename = f"mastered_mix_{timestamp}.wav"
    output_path = os.path.join(output_dir, output_filename)

    # Write the final mastered audio to a 24-bit WAV file.
    write(
        output_path,
        mastered_mix,
        samplerate=SAMPLE_RATE,
        subtype='PCM_24'
    )
    
    return output_path
