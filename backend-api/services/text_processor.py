import re
from typing import List

def split_text_into_chunks(text: str) -> List[str]:
    """Splits a text into logical chunks (e.g. sentences or paragraphs)."""
    # Split text into sentences using simple regex on punctuation boundaries
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]
