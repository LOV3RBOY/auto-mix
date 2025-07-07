from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class PromptSpec(BaseModel):
    """
    Defines the structured output from the Prompt Parser Service.
    """
    tempo: Optional[int] = Field(None, description="Tempo in BPM, from prompt.", example=174)
    key: Optional[str] = Field(None, description="Musical key, from prompt.", example="F# Minor")
    genre: Optional[str] = Field(None, description="Primary genre, from prompt.", example="drum and bass")
    instruments: List[str] = Field(default_factory=list, description="Requested instruments.", example=["drums", "reese bass"])
    style_references: List[str] = Field(default_factory=list, description="Artist or track style references.", example=["Pendulum"])
    mood: Optional[str] = Field(None, description="Desired mood or feel.", example="high-energy")

class Segment(BaseModel):
    """
    Defines the structure for a single musical segment from style analysis.
    """
    start_time: float = Field(..., description="Start time of the segment in seconds.", example=0.0)
    end_time: float = Field(..., description="End time of the segment in seconds.", example=30.0)
    label: str = Field(..., description="A label for the segment.", example="Intro")

class StyleFeatures(BaseModel):
    """
    Defines the JSON output from the Style Analysis Service.
    """
    tempo: float = Field(..., description="Tempo in BPM, from analysis.", example=174.05)
    key: str = Field(..., description="Musical key, from analysis.", example="F# Minor")
    segments: List[Segment] = Field(..., description="A list of structural segments found in the track.")

class GenerationRequest(BaseModel):
    """
    Defines the shape of the incoming request payload for the /generate endpoint.
    """
    prompt_spec: PromptSpec = Field(..., description="The structured output from the Prompt Parser Service.")
    style_features: Optional[StyleFeatures] = Field(None, description="The JSON output from the Style Analysis Service (optional).")

class GenerationResponse(BaseModel):
    """
    Defines the structured response for a successful generation request.
    """
    job_id: str = Field(..., description="Unique identifier for the generation job.")
    stems: Dict[str, str] = Field(..., description="A dictionary of generated audio stem file paths.", example={
        "drums": "/stems/job_xyz_drums.wav",
        "bass": "/stems/job_xyz_bass.wav",
        "synth": "/stems/job_xyz_synth.wav"
    })
