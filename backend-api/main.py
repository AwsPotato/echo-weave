import asyncio
import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas.request_schemas import ProcessTextRequest
from schemas.response_schemas import ProcessTextResponse, ProcessTextChunk, WordTiming, NovelfireResponse
from services.text_processor import split_text_into_chunks
from services.nlp_engine import detect_mood
from services.tts_engine import generate_audio
from config import settings
import httpx
from bs4 import BeautifulSoup

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

@app.get("/api/novelfire/chapter", response_model=NovelfireResponse)
async def get_novelfire_chapter(url: str) -> NovelfireResponse:
    if "novelfire.net" not in url:
        raise HTTPException(status_code=400, detail="Only novelfire.net URLs are supported.")
        
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_tag = soup.find('span', class_='chapter-title')
            title = title_tag.text.strip() if title_tag else "Unknown Chapter"
            
            # Extract content
            content_div = soup.find('div', id='content')
            if not content_div:
                raise HTTPException(status_code=404, detail="Could not find chapter content.")
                
            paragraphs = content_div.find_all('p')
            text_content = "\n\n".join(p.text.strip() for p in paragraphs if p.text.strip())
            
            return NovelfireResponse(title=title, content=text_content)
    except Exception as e:
        logger.error(f"Error fetching novelfire chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
