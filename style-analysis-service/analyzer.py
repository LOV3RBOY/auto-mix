import numpy as np
import librosa
from schemas import AnalysisResult, Segment
import logging

logger = logging.getLogger(__name__)

def estimate_key(y, sr):
    """
    Estimates the musical key of an audio track using a chromagram and key profiles.
    """
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    
    # Key profiles based on Krumhansl-Schmuckler
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    major_profile /= np.sum(major_profile)
    minor_profile /= np.sum(minor_profile)
    
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    keys = [note + ' Major' for note in notes] + [note + ' Minor' for note in notes]
    
    correlations = []
    for i in range(12):
        correlations.append(np.corrcoef(chroma_mean, np.roll(major_profile, i))[0, 1])
    for i in range(12):
        correlations.append(np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0, 1])

    best_key_index = np.argmax(correlations)
    return keys[best_key_index]


def segment_audio(y, sr, num_segments=10):
    """
    Performs structural segmentation on an audio track.
    """
    chroma_seg = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    try:
        margin_chroma = librosa.util.stack([chroma_seg, librosa.feature.spectral_centroid(y=y, sr=sr)])
        boundaries = librosa.segment.agglomerative(margin_chroma, k=num_segments)
        boundary_times = librosa.frames_to_time(boundaries, sr=sr)
    except Exception as e:
        logger.warning(f"Agglomerative segmentation failed: {e}. Falling back to fixed splitting.")
        duration = librosa.get_duration(y=y, sr=sr)
        boundary_times = np.linspace(0, duration, num_segments + 1)

    full_duration = librosa.get_duration(y=y, sr=sr)
    boundary_times = np.concatenate(([0], boundary_times, [full_duration]))
    boundary_times = np.unique(boundary_times)
    
    segments = []
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(len(boundary_times) - 1):
        start_time = boundary_times[i]
        end_time = boundary_times[i+1]
        if end_time > start_time + 0.5: # Only include segments longer than 0.5s
            segments.append(
                Segment(start_time=start_time, end_time=end_time, label=f"Part {labels[i % len(labels)]}")
            )
            
    return segments


def analyze_audio(file_path: str) -> AnalysisResult:
    """
    Main analysis function. Loads an audio file and extracts features.
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
    except Exception as e:
        raise IOError(f"Could not load audio file: {e}")

    # 1. Estimate Tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # 2. Estimate Key
    key = estimate_key(y, sr)
    
    # 3. Perform Segmentation
    segments = segment_audio(y, sr)
    
    return AnalysisResult(
        tempo=float(tempo),
        key=key,
        segments=segments
    )
