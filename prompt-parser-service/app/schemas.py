from pydantic import BaseModel, Field
from typing import List, Optional

class PromptRequest(BaseModel):
    """
    Defines the shape of the incoming request payload.
    """
    prompt: str = Field(..., description="The natural language prompt to be parsed.")

class StructuredPrompt(BaseModel):
    """
    Defines the structured output of the parsing service.
    All fields are optional as they may not be present in every prompt.
    """
    tempo: Optional[int] = Field(None, description="The beats per minute (BPM) of the track.", example=128)
    key: Optional[str] = Field(None, description="The musical key of the track.", example="C# Minor")
    genre: Optional[str] = Field(None, description="The primary genre of the track.", example="House")
    instruments: List[str] = Field(default_factory=list, description="A list of requested instruments.", example=["piano", "synth bass"])
    style_references: List[str] = Field(default_factory=list, description="A list of artist or track style references.", example=["Daft Punk", "Skrillex"])
    mood: Optional[str] = Field(None, description="The desired mood or feel of the track.", example="energetic")

    class Config:
        from_attributes = True
