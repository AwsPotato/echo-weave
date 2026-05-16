import hashlib
import os
import logging
import edge_tts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio_cache")

os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

# 6-tier contextual classification matrix
# Format: (Voice, Rate, Pitch)
# Using a single-narrator system with dynamic speech parameters
MOOD_PROFILES = {
    "neutral_narrative": ("en-US-AndrewNeural", "+0%", "+0Hz"),
    "ominous_suspense": ("en-US-AndrewNeural", "-15%", "-5Hz"),
    "high_action": ("en-US-AndrewNeural", "+15%", "+3Hz"),
    "analytical_inner": ("en-US-AndrewNeural", "+5%", "-2Hz"),
    "awe_astonishment": ("en-US-AndrewNeural", "-10%", "+2Hz"),
    "grim_savage": ("en-US-AndrewNeural", "-5%", "-8Hz")
}

async def generate_audio(text: str, mood: str) -> str:
    """
    Generates an audio file using edge-tts based on content and mood parameters.
    Returns the static URL for the generated file.
    """
    profile = MOOD_PROFILES.get(mood, MOOD_PROFILES["neutral_narrative"])
    voice, rate, pitch = profile
    
    # Include the profile parameters in the hash to avoid collisions if mood parameters change
    hash_input = f"{text}_{voice}_{rate}_{pitch}"
    text_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    filename = f"{text_hash}.mp3"
    filepath = os.path.join(AUDIO_CACHE_DIR, filename)
    
    if not os.path.exists(filepath):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(filepath)
        except Exception as e:
            logging.error(f"Failed to generate TTS for chunk. Error: {e}")
            raise RuntimeError(f"TTS Generation failed: {e}")
            
    return f"http://localhost:8000/static/{filename}"
