import re

MOOD_WEIGHTS = {
    "ominous_suspense": ["shadow", "darkness", "came alive", "fear", "stealth", "chill", "shiver", "sneak", "creeping"],
    "high_action": ["combat", "explosion", "charge", "slash", "shout", "fast", "devastation", "strike", "hit", "attack"],
    "analytical_inner": ["formation", "synergy", "understand", "calculate", "strategy", "evaluate", "observe", "plan", "logic"],
    "awe_astonishment": ["divine", "overwhelming", "massive", "frightening spectacle", "perfection", "god", "immense", "incredible"],
    "grim_savage": ["blood", "tearing flesh", "butchery", "scream", "agony", "brutal", "horror", "gore", "carnage"]
}

def detect_mood(text: str, previous_mood: str = "neutral_narrative") -> str:
    """
    Analyzes text using semantic weight and phrase matching.
    Inherits previous_mood if zero direct matches are found, unless a scene transition occurs.
    """
    text_lower = text.lower()
    
    # Scene transition detection to break out of inherited mood
    transition_markers = [r'\*\*\*', r'meanwhile', r'later', r'the next day', r'hours passed', r'suddenly']
    if any(re.search(marker, text_lower) for marker in transition_markers):
        previous_mood = "neutral_narrative"

    scores = {mood: 0 for mood in MOOD_WEIGHTS.keys()}
    
    # Calculate keyword/phrase weight
    for mood, keywords in MOOD_WEIGHTS.items():
        for kw in keywords:
            if kw in text_lower:
                # Give slightly more weight to phrases vs single words
                weight = 2 if " " in kw else 1
                scores[mood] += weight
                
    max_score = 0
    best_mood = previous_mood
    
    # Determine the mood with the highest weight
    for mood, score in scores.items():
        if score > max_score:
            max_score = score
            best_mood = mood
            
    # Fallback to inherited mood
    if max_score == 0:
        return previous_mood
        
    return best_mood
