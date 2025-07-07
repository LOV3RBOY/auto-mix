from pydantic import BaseModel, Field
from typing import List

class Segment(BaseModel):
    """Defines the structure for a single musical segment."""
    start_time: float = Field(..., description="Start time of the segment in seconds.", example=0.0)
    end_time: float = Field(..., description="End time of the segment in seconds.", example=15.5)
    label: str = Field(..., description="A generic label for the segment.", example="Part A")

class AnalysisResult(BaseModel):
    """Defines the structured output of the analysis service."""
    tempo: float = Field(..., description="Estimated tempo in beats per minute (BPM).", example=120.0)
    key: str = Field(..., description="Estimated musical key of the track.", example="C Major")
    segments: List[Segment] = Field(..., description="A list of structural segments found in the track.")

    class Config:
        from_attributes = True
