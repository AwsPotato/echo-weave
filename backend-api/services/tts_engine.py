import uuid

def generate_mock_audio(text: str, mood: str) -> str:
    """
    Simulates generating an audio file path based on content and mood.
    Ready to be replaced by OpenAI TTS or ElevenLabs integration.
    """
    mock_id = uuid.uuid4().hex[:8]
    return f"https://mock-tts-storage.local/audio/{mood}_{mock_id}.mp3"
