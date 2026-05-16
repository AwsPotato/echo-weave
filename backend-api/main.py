import asyncio
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas.request_schemas import ProcessTextRequest
from schemas.response_schemas import ProcessTextResponse, ProcessTextChunk
from services.text_processor import split_text_into_chunks
from services.nlp_engine import detect_mood
from services.tts_engine import generate_audio
from config import settings

logger = logging.getLogger("echo-weave")

app = FastAPI(title=settings.app_name, description="Smart Audio Pipeline")

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="audio_cache"), name="static")

@app.post("/api/process-text", response_model=ProcessTextResponse)
async def process_text(request: ProcessTextRequest) -> ProcessTextResponse:
    chunks = split_text_into_chunks(request.text)
    
    # Phase 1: Sequential mood detection (depends on previous mood state)
    chunk_moods: list[tuple[str, str]] = []
    previous_mood = "neutral_narrative"
    for chunk in chunks:
        mood = detect_mood(chunk, previous_mood)
        chunk_moods.append((chunk, mood))
        previous_mood = mood
    
    # Phase 2: Concurrent TTS generation via asyncio.gather
    start = time.perf_counter()
    
    tasks = [generate_audio(text, mood) for text, mood in chunk_moods]
    audio_urls: list[str] = await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start
    logger.info(f"Generated {len(audio_urls)} audio chunks in {elapsed:.2f} seconds")
    
    # Phase 3: Assemble ordered response
    result_chunks = [
        ProcessTextChunk(
            original_text=text,
            mood=mood,
            audio_url=audio_url
        )
        for (text, mood), audio_url in zip(chunk_moods, audio_urls)
    ]
        
    return ProcessTextResponse(chunks=result_chunks)
