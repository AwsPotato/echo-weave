from pydantic import BaseModel
from typing import List

class ProcessTextChunk(BaseModel):
    original_text: str
    mood: str
    audio_url: str

class ProcessTextResponse(BaseModel):
    chunks: List[ProcessTextChunk]
