import asyncio
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas.request_schemas import ProcessTextRequest
from schemas.response_schemas import ProcessTextResponse, ProcessTextChunk, WordTiming
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
    chunk_analysis: list[tuple[str, str, str]] = []  # (text, mood, weight)
    previous_mood = "neutral"
    for chunk in chunks:
        mood, weight = detect_mood(chunk, previous_mood)
        chunk_analysis.append((chunk, mood, weight))
        previous_mood = mood
    
    # Phase 2: Concurrent TTS generation via asyncio.gather
    start = time.perf_counter()
    
    tasks = [generate_audio(text, mood, weight) for text, mood, weight in chunk_analysis]
    results: list[tuple[str, list[dict]]] = await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start
    logger.info(f"Generated {len(results)} audio chunks in {elapsed:.2f} seconds")
    
    # Phase 3: Assemble ordered response
    result_chunks = [
        ProcessTextChunk(
            text=text,
            mood=mood,
            weight=weight,
            audio_url=audio_url,
            word_timings=[WordTiming(**wt) for wt in word_timings]
        )
        for (text, mood, weight), (audio_url, word_timings) in zip(chunk_analysis, results)
    ]
        
    return ProcessTextResponse(chunks=result_chunks)
