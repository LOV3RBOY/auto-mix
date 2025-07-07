import re
from typing import List, Optional, Dict, Any

from .schemas import StructuredPrompt

# These could be loaded from a config file or database in a real application.
KNOWN_GENRES = [
    "drum and bass", "dnb", "house", "techno", "trance", "dubstep", "hip hop",
    "ambient", "lo-fi", "synthwave", "trap", "pop", "rock", "jazz"
]
KNOWN_INSTRUMENTS = [
    "piano", "guitar", "bass", "drums", "synth", "vocal", "strings",
    "brass", "pads", "arp", "lead", "reese bass"
]
KNOWN_MOODS = [
    "high-energy", "energetic", "chill", "relaxed", "dark", "aggressive",
    "melancholic", "sad", "euphoric", "uplifting", "groovy", "funky"
]

KEY_REGEX = re.compile(
    r'in (?:the )?key of ([A-G][#b]? (?:major|minor|maj|min))|([A-G][#b]? (?:major|minor|maj|min))', 
    re.IGNORECASE
)
BPM_REGEX = re.compile(r'(\d{2,3})\s*bpm', re.IGNORECASE)
STYLE_REGEX = re.compile(r'in the style of ([\w\s-]+?)(?=\s+at|\s+in|\s+with|$|,)', re.IGNORECASE)


def _normalize_key(match: re.Match) -> str:
    """Normalizes a found key into a consistent format from regex match groups."""
    key_str = match.group(1) or match.group(2)
    if not key_str:
        return ""

    key_str = key_str.lower().replace('maj', 'major').replace('min', 'minor')
    parts = key_str.split()
    return " ".join([p[0].upper() + p[1:] for p in parts])

def parse_prompt(prompt: str) -> StructuredPrompt:
    """
    Parses a natural language prompt to extract musical entities using regex and keyword matching.
    """
    lower_prompt = prompt.lower()
    parsed_data: Dict[str, Any] = {
        "instruments": [],
        "style_references": [],
    }

    # 1. Extract BPM
    bpm_match = BPM_REGEX.search(lower_prompt)
    parsed_data["tempo"] = int(bpm_match.group(1)) if bpm_match else None

    # 2. Extract Key
    key_match = KEY_REGEX.search(lower_prompt)
    parsed_data["key"] = _normalize_key(key_match) if key_match else None

    # 3. Extract Style References
    style_match = STYLE_REGEX.search(lower_prompt)
    if style_match:
        parsed_data["style_references"].append(style_match.group(1).strip().title())

    # 4. Extract Genre (first match wins)
    parsed_data["genre"] = next((genre for genre in KNOWN_GENRES if re.search(r'\b' + re.escape(genre) + r'\b', lower_prompt)), None)

    # 5. Extract Instruments
    for instrument in KNOWN_INSTRUMENTS:
        if re.search(r'\b' + re.escape(instrument) + r'\b', lower_prompt):
            parsed_data["instruments"].append(instrument)

    # 6. Extract Mood (first match wins)
    parsed_data["mood"] = next((mood for mood in KNOWN_MOODS if re.search(r'\b' + re.escape(mood).replace('-', r'\s*-?\s*') + r'\b', lower_prompt)), None)
            
    return StructuredPrompt(**parsed_data)
