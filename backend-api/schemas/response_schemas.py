from pydantic import BaseModel
from typing import List

class ProcessTextChunk(BaseModel):
    text: str
    mood: str
    weight: str
    audio_url: str

class ProcessTextResponse(BaseModel):
    chunks: List[ProcessTextChunk]
