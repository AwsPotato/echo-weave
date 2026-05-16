from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.request_schemas import ProcessTextRequest
from schemas.response_schemas import ProcessTextResponse, ProcessTextChunk
from services.text_processor import split_text_into_chunks
from services.nlp_engine import detect_mood
from services.tts_engine import generate_mock_audio
from config import settings

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

@app.post("/api/process-text", response_model=ProcessTextResponse)
def process_text(request: ProcessTextRequest) -> ProcessTextResponse:
    chunks = split_text_into_chunks(request.text)
    
    result_chunks = []
    for chunk in chunks:
        mood = detect_mood(chunk)
        audio_url = generate_mock_audio(chunk, mood)
        
        result_chunks.append(
            ProcessTextChunk(
                original_text=chunk,
                mood=mood,
                audio_url=audio_url
            )
        )
        
    return ProcessTextResponse(chunks=result_chunks)
