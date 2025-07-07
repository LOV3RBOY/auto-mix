from pydantic import BaseModel, Field
from typing import List

class MixingRequest(BaseModel):
    stem_paths: List[str] = Field(
        ...,
        description="A list of absolute file paths to the audio stems inside the container.",
        example=[
            "/app/audio_files/drums.wav",
            "/app/audio_files/bass.wav",
            "/app/audio_files/synth.wav"
        ]
    )

class MixingResponse(BaseModel):
    output_path: str = Field(
        ...,
        description="The absolute file path of the final mixed and mastered audio file.",
        example="/app/audio_files/mastered_mix_1657843200.wav"
    )
    message: str = Field(
        ...,
        description="A status message confirming the result of the operation.",
        example="Mixing and mastering complete. Output saved."
    )

