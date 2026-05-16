import re
from typing import Tuple

MOOD_KEYWORDS: dict[str, list[str]] = {

    "hype": [
        # --- Core Energy & Excitement ---
        "amazing", "incredible", "awesome", "fantastic", "epic", "legendary",
        "unbelievable", "insane", "hype", "excited", "thrilled", "celebrate",
        "victory", "triumph", "magnificent", "glorious", "wow", "brilliant",
        "spectacular", "phenomenal", "extraordinary", "marvelous", "stunning",
        "electrifying", "exhilarating", "sensational", "breathtaking",
        # --- Achievement & Glory ---
        "champion", "conquer", "conquered", "unstoppable", "invincible",
        "undefeated", "crowned", "gloriously", "heroic", "heroically",
        "transcended", "surpassed", "exceeded", "shattered records",
        "broke through", "overcame", "prevailed", "dominated", "crushed it",
        "nailed it", "aced it", "knocked it out of the park",
        # --- Celebration & Joy ---
        "cheered", "roared with approval", "erupted", "jubilant", "euphoric",
        "ecstatic", "elated", "overjoyed", "rapturous", "blissful",
        "celebration", "festive", "rejoice", "rejoicing", "party",
        "fireworks", "confetti", "standing ovation", "applause",
        # --- Power & Ascension ---
        "power up", "level up", "evolved", "awakened", "unleashed",
        "ascended", "transcendence", "transformation", "metamorphosis",
        "breakthrough", "revelation", "epiphany", "enlightened",
        "pinnacle", "zenith", "apex", "summit", "crowning moment",
        # --- Sports & Competition ---
        "goal", "scored", "winning", "championship", "finals",
        "knockout", "slam dunk", "home run", "checkmate", "flawless victory",
        "perfect score", "record-breaking", "personal best",
        # --- Fantasy/Sci-Fi Hype ---
        "legendary weapon", "ultimate form", "final form", "super saiyan",
        "chosen one", "prophecy fulfilled", "destiny", "fate aligned",
        "sacred power", "ancient magic", "divine blessing",
        "warp speed", "hyperdrive", "shields up", "maximum power",
    ],

    "tense": [
        # --- Core Suspense ---
        "shadow", "darkness", "fear", "danger", "creeping", "lurking", "shiver",
        "dread", "nervous", "anxious", "uneasy", "ominous", "sinister", "looming",
        "suspense", "chilling", "eerie", "foreboding", "menacing",
        # --- Stealth & Infiltration ---
        "sneaking", "crouching", "hiding", "concealed", "stalking", "prowling",
        "silent", "silently", "tiptoe", "hushed", "muffled", "stealthy",
        "camouflaged", "invisible", "undetected", "surveillance", "espionage",
        "undercover", "covert", "infiltrate", "infiltration", "sabotage",
        # --- Psychological Tension ---
        "paranoid", "paranoia", "suspicion", "suspicious", "distrust",
        "watched", "followed", "someone behind", "eyes on me", "being watched",
        "trapped", "cornered", "no escape", "no way out", "dead end",
        "claustrophobic", "suffocating", "closing in", "walls closing",
        "ticking clock", "countdown", "running out of time", "deadline",
        # --- Horror & Dread ---
        "haunted", "haunting", "ghostly", "spectral", "apparition",
        "phantom", "wraith", "poltergeist", "possession", "possessed",
        "cursed", "curse", "hex", "omen", "premonition", "vision",
        "nightmare", "night terror", "sleep paralysis", "insomnia",
        "something moved", "what was that", "did you hear that",
        "footsteps", "breathing", "whisper", "whispered", "murmur",
        # --- Environmental Tension ---
        "fog", "mist", "haze", "storm approaching", "thunder rumbled",
        "lightning cracked", "wind howled", "rain pounded", "pitch black",
        "moonless", "abandoned", "desolate", "decrepit", "crumbling",
        "flickering", "dimly lit", "candlelight", "lantern", "torch",
        # --- Thriller/Crime ---
        "evidence", "crime scene", "fingerprints", "blood trail",
        "witness", "testimony", "alibi", "motive", "suspect",
        "interrogation", "confession", "guilty", "innocent",
        "verdict", "jury", "courtroom", "detective", "investigation",
        # --- Military/War Tension ---
        "ambush", "flank", "perimeter", "reconnaissance", "scout",
        "patrol", "sentry", "lookout", "enemy territory", "behind enemy lines",
        "minefield", "tripwire", "booby trap", "sniper", "crosshairs",
        "incoming", "take cover", "hold position", "stand by",
    ],

    "angry": [
        # --- Core Rage ---
        "furious", "rage", "hate", "destroy", "smash", "shout", "scream",
        "roar", "wrath", "vengeance", "crush", "slammed", "cursed", "fury",
        "seething", "livid", "outrage", "outraged", "infuriated",
        # --- Physical Aggression ---
        "punched", "kicked", "struck", "slapped", "throttled", "choked",
        "strangled", "pummeled", "battered", "beaten", "thrashed",
        "demolished", "obliterated", "annihilated", "decimated",
        "ripped apart", "torn to shreds", "smashed to pieces",
        "clenched fists", "gritted teeth", "jaw clenched", "veins bulging",
        "fist through the wall", "flipped the table", "threw across the room",
        # --- Verbal Aggression ---
        "yelled", "screamed", "bellowed", "thundered", "snarled", "growled",
        "barked", "snapped", "hissed", "spat", "shouted", "hollered",
        "exploded", "lashed out", "went off", "lost it", "blew up",
        "tirade", "rant", "ranting", "berating", "condemned", "denounced",
        # --- Emotional Intensity ---
        "betrayed", "betrayal", "treachery", "backstabbed", "double-crossed",
        "lied", "deceived", "manipulated", "exploited", "used",
        "disgusted", "revolted", "repulsed", "contempt", "loathing",
        "despised", "abhorred", "detested", "resented", "resentment",
        "bitter", "bitterness", "spiteful", "vindictive", "malicious",
        # --- Fantasy/Action Anger ---
        "battle cry", "war cry", "charge", "assault", "onslaught",
        "rampage", "berserker", "berserk", "frenzy", "frenzied",
        "bloodlust", "killing intent", "murderous aura", "death glare",
        "unforgivable", "how dare you", "you will pay", "I will end you",
        # --- Injustice ---
        "unfair", "unjust", "corruption", "oppression", "tyranny",
        "exploitation", "inequality", "discrimination", "persecution",
        "silenced", "suppressed", "censored", "marginalized",
    ],

    "sad": [
        # --- Core Sadness ---
        "tears", "weep", "sorrow", "grief", "loss", "mourning", "lonely",
        "heartbroken", "melancholy", "despair", "tragic", "anguish", "sobbing",
        "farewell", "goodbye", "regret", "suffering", "misery",
        # --- Grief & Death ---
        "funeral", "burial", "grave", "tombstone", "cemetery", "eulogy",
        "passed away", "died", "death", "deceased", "memorial",
        "lost forever", "never coming back", "gone", "departed",
        "widowed", "orphaned", "bereaved", "in memoriam",
        "rest in peace", "final breath", "last words", "deathbed",
        # --- Loneliness & Isolation ---
        "alone", "isolated", "abandoned", "forsaken", "forgotten",
        "nobody", "no one", "empty", "hollow", "void", "numb",
        "disconnected", "estranged", "outcast", "exile", "exiled",
        "solitude", "solitary", "desolate", "deserted", "wandering",
        "homeless", "drifting", "aimless", "purposeless", "lost",
        # --- Emotional Pain ---
        "heartache", "pain", "hurting", "wounded", "scarred",
        "broken", "shattered", "crushed", "devastated", "destroyed",
        "inconsolable", "distraught", "wretched", "tormented",
        "haunted by memories", "couldn't forget", "lingering pain",
        "heavy heart", "weight on shoulders", "burden", "carrying",
        # --- Romance Sadness ---
        "breakup", "divorce", "separation", "unrequited", "unrequited love",
        "rejection", "rejected", "moved on", "left behind", "let go",
        "couldn't save", "too late", "if only", "what could have been",
        "never meant to be", "star-crossed", "doomed", "forbidden love",
        # --- Nostalgia & Longing ---
        "nostalgia", "nostalgic", "reminisce", "remember when",
        "those days", "used to be", "once upon a time", "childhood",
        "homesick", "yearning", "longing", "pining", "wistful",
        "bittersweet", "faded", "withered", "wilted", "decayed",
        # --- Weather/Nature (Pathetic Fallacy) ---
        "rain fell", "rain poured", "grey skies", "overcast",
        "wilting", "autumn leaves", "falling petals", "winter",
        "cold wind", "frost", "frozen", "barren", "bare branches",
    ],

    "sarcastic": [
        # --- Core Sarcasm ---
        "obviously", "clearly", "sure", "brilliant", "genius", "wonderful",
        "of course", "how lovely", "oh great", "how nice", "what a surprise",
        "as if", "yeah right", "totally", "absolutely",
        # --- Dismissive ---
        "whatever", "big deal", "who cares", "cry me a river",
        "boo hoo", "my heart bleeds", "how tragic", "poor baby",
        "spare me", "give me a break", "get over it", "move along",
        "nothing to see here", "shocking", "I'm shocked",
        # --- Faux Compliments ---
        "oh how wonderful", "what a delight", "how charming",
        "how original", "never seen that before", "groundbreaking",
        "revolutionary", "truly inspiring", "masterpiece", "work of art",
        "real winner", "top notch", "first rate", "gold star",
        "slow clap", "bravo", "well done", "congratulations",
        # --- Deadpan / Dry Wit ---
        "thrilling", "riveting", "fascinating", "enthralling",
        "edge of my seat", "can't contain my excitement",
        "be still my beating heart", "I can hardly wait",
        "what joy", "what fun", "lucky me", "my lucky day",
        "just my luck", "typical", "predictable", "surprise surprise",
        "who would have thought", "imagine that", "fancy that",
        # --- Rhetorical ---
        "you think", "you don't say", "no kidding", "really now",
        "is that so", "do tell", "pray tell", "enlighten me",
        "please continue", "I'm all ears", "by all means",
        "after you", "be my guest", "help yourself",
        # --- Self-Deprecating ---
        "story of my life", "just my style", "classic me",
        "wouldn't be me if", "par for the course",
        "another day another disaster", "living the dream",
    ],

    "thoughtful": [
        # --- Core Reflection ---
        "perhaps", "consider", "wonder", "ponder", "reflect", "question",
        "understand", "realize", "thought", "meaning", "philosophy", "observe",
        "evaluate", "strategy", "logic", "analyze", "contemplate",
        # --- Intellectual Analysis ---
        "hypothesis", "theory", "theorem", "equation", "formula",
        "variable", "constant", "correlation", "causation", "deduction",
        "induction", "inference", "conclusion", "evidence", "data",
        "pattern", "anomaly", "outlier", "deviation", "trend",
        "probability", "likelihood", "possibility", "uncertainty",
        # --- Decision Making ---
        "decision", "choice", "dilemma", "trade-off", "compromise",
        "weigh the options", "pros and cons", "risk assessment",
        "calculated", "deliberate", "intentional", "strategic",
        "tactical", "methodical", "systematic", "meticulous",
        "careful", "cautious", "prudent", "measured", "balanced",
        # --- Philosophical & Existential ---
        "existence", "purpose", "identity", "consciousness", "awareness",
        "morality", "ethics", "virtue", "justice", "truth",
        "freedom", "determinism", "fate", "free will", "choice",
        "paradox", "contradiction", "irony", "absurdity",
        "what does it mean", "why do we", "who are we",
        "the nature of", "in the grand scheme",
        # --- Inner Monologue ---
        "wondered", "mused", "pondered", "contemplated", "mulled over",
        "turned over in mind", "couldn't stop thinking", "nagging feeling",
        "something didn't add up", "pieces of the puzzle",
        "the more I thought", "it occurred to me", "dawned on me",
        "began to see", "slowly understood", "came to realize",
        # --- Observation & Perception ---
        "noticed", "observed", "detected", "sensed", "perceived",
        "recognized", "identified", "distinguished", "discerned",
        "scrutinized", "examined", "inspected", "studied", "surveyed",
        "panoramic", "bird's eye", "perspective", "viewpoint", "lens",
        # --- Memory & Wisdom ---
        "remembered", "recalled", "recollected", "reminisced",
        "lesson", "wisdom", "experience", "hindsight", "foresight",
        "intuition", "instinct", "gut feeling", "sixth sense",
        "ancient knowledge", "passed down", "generations",
        "proverb", "saying", "adage", "axiom", "maxim",
        # --- Science Fiction Thoughtfulness ---
        "simulation", "algorithm", "neural network", "quantum",
        "singularity", "multiverse", "dimension", "timeline",
        "parallel universe", "alternate reality", "temporal",
        "cybernetic", "synthetic", "artificial intelligence",
    ],
}

# Intensity amplifiers: words/patterns that push weight upward
INTENSITY_AMPLIFIERS: list[str] = [
    "very", "extremely", "absolutely", "utterly", "completely", "totally",
    "incredibly", "overwhelmingly", "devastatingly", "unimaginably",
    "profoundly", "deeply", "immensely", "enormously", "tremendously",
    "fiercely", "violently", "savagely", "brutally", "viciously",
    "desperately", "frantically", "wildly", "insanely", "madly",
    "unbearably", "excruciatingly", "agonizingly", "painfully",
    "impossibly", "incomprehensibly", "indescribably", "unspeakably",
    "relentlessly", "mercilessly", "ruthlessly", "unforgivingly",
    "terrifyingly", "horrifyingly", "nightmarishly", "hellishly",
    "blindingly", "deafeningly", "thunderously", "explosively",
    "infinitely", "eternally", "perpetually", "endlessly",
    "heart-wrenchingly", "gut-wrenchingly", "soul-crushingly",
    "mind-blowingly", "jaw-droppingly", "earth-shatteringly",
    "beyond", "sheer", "pure", "raw", "nothing but",
]


def _count_caps_words(text: str) -> int:
    """Count ALL-CAPS words (3+ chars) as intensity signals."""
    return sum(1 for word in text.split() if word.isupper() and len(word) >= 3)


def _count_exclamations(text: str) -> int:
    """Count exclamation marks as intensity signals."""
    return text.count("!")


def _determine_weight(keyword_hits: int, caps_count: int, exclamation_count: int, amplifier_hits: int) -> str:
    """Translate raw signal counts into a low/medium/high weight."""
    score: int = keyword_hits + caps_count + (exclamation_count * 2) + amplifier_hits

    if score >= 6:
        return "high"
    elif score >= 3:
        return "medium"
    return "low"


def detect_mood(text: str, previous_mood: str = "neutral") -> Tuple[str, str]:
    """
    Analyzes text for mood and intensity weight.
    Returns a tuple of (mood, weight).
    Inherits previous mood on zero matches unless a scene transition is detected.
    """
    text_lower: str = text.lower()

    # Scene transition detection resets inherited mood
    transition_markers: list[str] = [r"\*\*\*", r"meanwhile", r"later that", r"the next day", r"hours passed"]
    if any(re.search(marker, text_lower) for marker in transition_markers):
        previous_mood = "neutral"

    # Score each mood
    scores: dict[str, int] = {mood: 0 for mood in MOOD_KEYWORDS}
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                weight = 2 if " " in kw else 1
                scores[mood] += weight

    # Global intensity signals
    caps_count: int = _count_caps_words(text)
    exclamation_count: int = _count_exclamations(text)
    amplifier_hits: int = sum(1 for amp in INTENSITY_AMPLIFIERS if amp in text_lower)

    # Find dominant mood
    max_score: int = 0
    best_mood: str = previous_mood
    for mood, score in scores.items():
        if score > max_score:
            max_score = score
            best_mood = mood

    # Fallback: inherit previous mood with low weight
    if max_score == 0:
        return (previous_mood, "low")

    weight: str = _determine_weight(max_score, caps_count, exclamation_count, amplifier_hits)
    return (best_mood, weight)

def detect_word_mood(word: str, chunk_mood: str, chunk_weight: str) -> Tuple[str, str]:
    """
    Determines the specific mood and weight for an individual word.
    Falls back to the chunk's mood and weight if the word itself doesn't strongly signal an emotion.
    """
    clean_word = re.sub(r'[^a-zA-Z0-9]', '', word.lower())
    
    if not clean_word:
        return (chunk_mood, chunk_weight)

    is_caps = word.isupper() and len(clean_word) >= 3
    is_exclamation = "!" in word
    is_amplifier = clean_word in INTENSITY_AMPLIFIERS

    for mood, keywords in MOOD_KEYWORDS.items():
        # Check if clean_word exactly matches any single-word keyword or is a substring of a multi-word keyword
        # To be safe, just check exact match in the keywords list (which contains some single words)
        # or if the word is part of a multi-word keyword
        if clean_word in keywords or any(clean_word in kw.split() for kw in keywords):
            weight = "high" if (is_caps or is_exclamation or is_amplifier) else "medium"
            return (mood, weight)
            
    if is_amplifier or is_caps or is_exclamation:
        return (chunk_mood, "high")
        
    return (chunk_mood, chunk_weight)

