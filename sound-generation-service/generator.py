import asyncio
import logging
import uuid
from typing import Dict, Any

from schemas import GenerationRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SIMULATED_DELAY_SECONDS = 5

async def mock_generate_stems(request: GenerationRequest) -> Dict[str, Any]:
    """
    Simulates the audio generation process.
    """
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    prompt = request.prompt_spec
    log_message_parts = [f"Received job {job_id}: Generate track"]
    
    if prompt.genre:
        log_message_parts.append(f"in genre '{prompt.genre}'")
    
    # Prefer the more accurate key from style analysis if available
    if request.style_features and request.style_features.key:
         log_message_parts.append(f"in key of {request.style_features.key}")
    elif prompt.key:
        log_message_parts.append(f"in key of {prompt.key}")
    
    # Prefer the more accurate tempo from style analysis
    if request.style_features and request.style_features.tempo:
        log_message_parts.append(f"at {request.style_features.tempo:.0f} BPM")
    elif prompt.tempo:
        log_message_parts.append(f"at {prompt.tempo} BPM")
        
    if prompt.style_references:
        log_message_parts.append(f"in the style of {', '.join(prompt.style_references)}")

    logger.info(" ".join(log_message_parts))

    logger.info(f"[{job_id}] Simulating generation... process will take {SIMULATED_DELAY_SECONDS} seconds.")
    await asyncio.sleep(SIMULATED_DELAY_SECONDS)
    
    # Determine which stems to generate based on the prompt's instrument list.
    # If the list is empty, default to a standard set of instruments.
    instruments_to_generate = prompt.instruments if prompt.instruments else ["drums", "bass", "synth", "lead"]
    
    stems = {
        instrument: f"/stems/{job_id}_{instrument.replace(' ', '_')}.wav"
        for instrument in instruments_to_generate
    }
    
    logger.info(f"[{job_id}] Successfully generated {len(stems)} stems.")

    return {"job_id": job_id, "stems": stems}
