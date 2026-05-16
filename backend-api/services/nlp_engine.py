def detect_mood(text: str) -> str:
    """Analyzes text for specific keywords to detect atmospheric tone."""
    text_lower = text.lower()
    
    suspense_keywords = {"dark", "shadow", "quiet", "creep", "fear", "silent"}
    action_keywords = {"run", "shouted", "struck", "fast", "hit", "jump"}
    
    # Simple logic checking for intersection of words
    # Tokenize the input string roughly
    words = set(text_lower.replace(".", "").replace(",", "").replace("!", "").replace("?", "").split())
    
    if words.intersection(suspense_keywords):
        return "suspense"
    if words.intersection(action_keywords):
        return "action"
    
    return "neutral"
