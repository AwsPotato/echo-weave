import hashlib
import os
import logging
import edge_tts

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_CACHE_DIR: str = os.path.join(BASE_DIR, "audio_cache")

os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

logger = logging.getLogger("echo-weave.tts")

# Single narrator voice for the entire pipeline
NARRATOR_VOICE: str = "en-US-AndrewNeural"

# (mood, weight) -> (rate, pitch) lookup matrix
AUDIO_PROFILE_MATRIX: dict[tuple[str, str], tuple[str, str]] = {
    # neutral
    ("neutral", "low"):       ("+0%",   "+0Hz"),
    ("neutral", "medium"):    ("+0%",   "+0Hz"),
    ("neutral", "high"):      ("+0%",   "+0Hz"),
    # hype
    ("hype", "low"):          ("+5%",   "+1Hz"),
    ("hype", "medium"):       ("+12%",  "+3Hz"),
    ("hype", "high"):         ("+20%",  "+5Hz"),
    # tense
    ("tense", "low"):         ("-5%",   "-2Hz"),
    ("tense", "medium"):      ("-12%",  "-4Hz"),
    ("tense", "high"):        ("-18%",  "-6Hz"),
    # angry
    ("angry", "low"):         ("+5%",   "-2Hz"),
    ("angry", "medium"):      ("+10%",  "-4Hz"),
    ("angry", "high"):        ("+15%",  "-6Hz"),
    # sad
    ("sad", "low"):           ("-5%",   "-1Hz"),
    ("sad", "medium"):        ("-10%",  "-3Hz"),
    ("sad", "high"):          ("-18%",  "-5Hz"),
    # sarcastic
    ("sarcastic", "low"):     ("+3%",   "+2Hz"),
    ("sarcastic", "medium"):  ("+5%",   "+4Hz"),
    ("sarcastic", "high"):    ("+8%",   "+6Hz"),
    # thoughtful
    ("thoughtful", "low"):    ("-3%",   "-1Hz"),
    ("thoughtful", "medium"): ("+0%",   "-2Hz"),
    ("thoughtful", "high"):   ("+5%",   "-3Hz"),
}

# Default fallback profile
DEFAULT_PROFILE: tuple[str, str] = ("+0%", "+0Hz")


async def generate_audio(text: str, mood: str, weight: str) -> str:
    """
    Generates an audio file using edge-tts with dynamic rate/pitch
    scaled by the (mood, weight) combination.
    Returns the static URL for the generated file.
    """
    rate, pitch = AUDIO_PROFILE_MATRIX.get((mood, weight), DEFAULT_PROFILE)

    # Include mood+weight in hash so profile changes invalidate cache
    hash_input: str = f"{text}_{NARRATOR_VOICE}_{rate}_{pitch}"
    text_hash: str = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    filename: str = f"{text_hash}.mp3"
    filepath: str = os.path.join(AUDIO_CACHE_DIR, filename)

    if not os.path.exists(filepath):
        try:
            communicate = edge_tts.Communicate(text, NARRATOR_VOICE, rate=rate, pitch=pitch)
            await communicate.save(filepath)
        except Exception as e:
            logger.error(f"TTS generation failed for mood={mood}, weight={weight}: {e}")
            raise RuntimeError(f"TTS Generation failed: {e}")

    return f"http://localhost:8000/static/{filename}"
