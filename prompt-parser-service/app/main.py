from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from .schemas import PromptRequest, StructuredPrompt
from .parser import parse_prompt

app = FastAPI(
    title="AI Music Production Assistant - Prompt Parser",
    description="A service to parse natural language music prompts into a structured format.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file to locate index.html
static_files_dir = os.path.dirname(os.path.abspath(__file__))

@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(static_files_dir, '../index.html'))

@app.get("/script.js", include_in_schema=False)
async def read_script():
    return FileResponse(os.path.join(static_files_dir, '../script.js'))


@app.post("/api/v1/parse", response_model=StructuredPrompt, tags=["Parsing"])
async def create_parsed_prompt(request: PromptRequest):
    """
    Accepts a natural language prompt and returns a structured representation.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        structured_prompt = parse_prompt(request.prompt)
        return structured_prompt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
