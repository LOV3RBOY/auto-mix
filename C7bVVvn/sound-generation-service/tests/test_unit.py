import pytest
from .generator import mock_generate_stems
from .schemas import GenerationRequest, PromptSpec

@pytest.mark.asyncio
async def test_generate_with_specific_instruments():
    """Test generation when specific instruments are requested."""
    prompt_spec = PromptSpec(instruments=["drums", "bass", "vocal chops"])
    request = GenerationRequest(prompt_spec=prompt_spec)
    
    result = await mock_generate_stems(request)
    
    assert "job_id" in result
    assert "stems" in result
    
    stems = result["stems"]
    assert len(stems) == 3
    assert "drums" in stems
    assert "bass" in stems
    assert "vocal_chops" in stems["vocal chops"] # Check space handling

@pytest.mark.asyncio
async def test_generate_with_default_instruments():
    """Test generation when no instruments are requested, using defaults."""
    prompt_spec = PromptSpec(instruments=[]) # Empty list
    request = GenerationRequest(prompt_spec=prompt_spec)
    
    result = await mock_generate_stems(request)
    
    stems = result["stems"]
    assert len(stems) == 4
    assert "drums" in stems
    assert "bass" in stems
    assert "synth" in stems
    assert "lead" in stems
    
@pytest.mark.asyncio
async def test_generate_returns_valid_structure():
    """Test that the response structure is always correct."""
    prompt_spec = PromptSpec()
    request = GenerationRequest(prompt_spec=prompt_spec)
    
    result = await mock_generate_stems(request)

    assert isinstance(result, dict)
    assert "job_id" in result
    assert isinstance(result["job_id"], str)
    assert "stems" in result
    assert isinstance(result["stems"], dict)
    
    # Check that paths look like paths
    for instrument, path in result["stems"].items():
        assert path.startswith("/stems/")
        assert path.endswith(".wav")
