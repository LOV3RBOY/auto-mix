import pytest
from app.parser import parse_prompt
from app.schemas import StructuredPrompt

@pytest.mark.parametrize("prompt, expected", [
    (
        "A high-energy drum and bass track at 174 bpm in the style of Pendulum, with a heavy reese bass in F# minor",
        StructuredPrompt(tempo=174, key="F# Minor", genre="drum and bass", instruments=["bass"], style_references=["Pendulum"], mood="high-energy")
    ),
    (
        "128bpm house music with a groovy bassline and piano chords",
        StructuredPrompt(tempo=128, key=None, genre="house", instruments=["piano", "bass"], style_references=[], mood="groovy")
    ),
    (
        "A chill lo-fi track in C major",
        StructuredPrompt(tempo=None, key="C Major", genre="lo-fi", instruments=[], style_references=[], mood="chill")
    ),
    (
        "Just a simple rock beat",
        StructuredPrompt(tempo=None, key=None, genre="rock", instruments=[], style_references=[], mood=None)
    ),
    (
        "",
        StructuredPrompt(tempo=None, key=None, genre=None, instruments=[], style_references=[], mood=None)
    ),
     (
        "Make something like Daft Punk",
        StructuredPrompt(style_references=["Daft Punk"])
    ),
])
def test_parse_prompt(prompt, expected):
    """Test the prompt parser with various inputs."""
    result = parse_prompt(prompt)
    
    # Pydantic models are compared by value, which is convenient
    assert result == expected

def test_key_normalization():
    """Test that different key formats are normalized correctly."""
    prompt1 = "a song in c# min"
    prompt2 = "a song in C# minor"
    prompt3 = "a song in the key of c# minor"
    
    expected = StructuredPrompt(key="C# Minor")
    
    assert parse_prompt(prompt1).key == expected.key
    assert parse_prompt(prompt2).key == expected.key
    assert parse_prompt(prompt3).key == expected.key
