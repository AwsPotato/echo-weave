from pydantic import BaseModel
from typing import List

class WordTiming(BaseModel):
    word: str
    offset: float
    duration: float
    mood: str = "neutral"
    weight: str = "low"

class ProcessTextChunk(BaseModel):
    text: str
    mood: str
    weight: str
    audio_url: str
    word_timings: List[WordTiming]

class ProcessTextResponse(BaseModel):
    chunks: List[ProcessTextChunk]
