<div align="center">

# 🔊 Echo-Weave

### Smart Audio Pipeline

*Transform text into adaptive, mood-aware audio experiences with real-time word highlighting.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

</div>

---

## Overview

Echo-Weave is a full-stack smart audio pipeline that takes raw text — book chapters, scripts, stories — and transforms it into a narrated audio experience with **mood-adaptive voice modulation** and **real-time word-by-word highlighting**.

Paste in any text, and the system will:

1. **Chunk** it into logical sentences.
2. **Analyze** each chunk for emotional tone using a weighted NLP heuristic engine.
3. **Generate** speech audio using Microsoft Edge TTS with dynamic voice parameters (rate, pitch) that shift based on the detected mood and intensity.
4. **Present** an interactive timeline UI with color-coded mood cards, inline playback, word highlighting, and auto-scroll.

---

## Features

### 🧠 Intelligent NLP Mood Detection
- **7-mood taxonomy**: `neutral`, `hype`, `tense`, `angry`, `sad`, `sarcastic`, `thoughtful`
- **3-tier intensity weighting**: `low`, `medium`, `high` — derived from keyword density, ALL-CAPS detection, exclamation marks, and amplifier words
- **300+ keyword dictionary** covering Fantasy, Sci-Fi, Horror, Romance, Thriller, Mystery, War, and more
- **Contextual inheritance**: chunks with no direct matches inherit the previous chunk's mood for smooth emotional flow
- **Scene transition detection**: markers like `***` or `"Meanwhile"` reset the inherited mood

### 🎙️ Single-Narrator Voice Modulation
- Locked to one premium voice (`en-US-AndrewNeural`) for consistent narrator identity
- **21-entry (mood × weight) audio profile matrix** that dynamically scales `rate` and `pitch`:
  - `tense + high` → `-18% rate, -6Hz pitch` (slow, deep, dread)
  - `hype + high` → `+20% rate, +5Hz pitch` (fast, energetic)
  - `sad + high` → `-18% rate, -5Hz pitch` (slow, somber)
- MD5-hashed audio caching with automatic invalidation when voice parameters change

### ✨ Real-Time Word Highlighting
- Word-level timing data captured from `edge-tts` `WordBoundary` events during generation
- `requestAnimationFrame`-based tracking for ~60fps smooth word highlighting
- Already-read words dim, the active word glows, upcoming words remain neutral

### 🎶 Interactive Timeline UI
- Color-coded chunk cards based on mood (emerald, indigo, rose, blue, amber, cyan, slate)
- **Play from any chunk**: click any timeline dot or play button to start sequential playback from that point
- **Play All**: one-click full narration from start to finish
- **Playback speed**: 0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x
- **Follow mode**: auto-scrolls the viewport to keep the active word centered on screen
- Progress bar showing current position in the timeline

### ⚡ Async Performance
- `asyncio.gather` fires all TTS generation concurrently — 10 chunks generate in ~2s instead of ~20s
- Audio files cached to disk with companion JSON timing metadata
- FastAPI static file serving for instant playback

---

## Architecture

```
Echo-Weave/
├── backend-api/                  # Python FastAPI backend
│   ├── main.py                   # API routes, CORS, static mount
│   ├── config.py                 # Environment config (pydantic-settings)
│   ├── requirements.txt          # Python dependencies
│   ├── audio_cache/              # Generated .mp3 + timing .json files
│   ├── schemas/
│   │   ├── request_schemas.py    # Pydantic request models
│   │   └── response_schemas.py   # Pydantic response models + WordTiming
│   └── services/
│       ├── text_processor.py     # Sentence boundary splitter
│       ├── nlp_engine.py         # Mood + weight detection engine
│       └── tts_engine.py         # edge-tts generation + word timing capture
│
└── frontend-ui/                  # Next.js TypeScript frontend
    └── app/
        ├── layout.tsx            # Root layout
        ├── globals.css           # Tailwind CSS config
        └── page.tsx              # Main dashboard UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| **TTS Engine** | edge-tts (Microsoft Edge Neural Voices) |
| **Frontend** | Next.js 16, React 19, TypeScript |
| **Styling** | Tailwind CSS |
| **Icons** | Lucide React |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone the repository

```bash
git clone https://github.com/AwsPotato/echo-weave.git
cd echo-weave
```

### 2. Start the Backend

```bash
cd backend-api

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install edge-tts

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. You can explore the auto-generated docs at `http://localhost:8000/docs`.

### 3. Start the Frontend

```bash
cd frontend-ui

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The UI will be available at `http://localhost:3000`.

---

## API Reference

### `POST /api/process-text`

Processes a block of text into mood-analyzed, audio-generated chunks.

**Request Body:**

```json
{
  "text": "The shadows crept along the wall. He shouted and charged forward!"
}
```

**Response:**

```json
{
  "chunks": [
    {
      "text": "The shadows crept along the wall.",
      "mood": "tense",
      "weight": "medium",
      "audio_url": "http://localhost:8000/static/a1b2c3d4.mp3",
      "word_timings": [
        { "word": "The", "offset": 0.05, "duration": 0.15 },
        { "word": "shadows", "offset": 0.22, "duration": 0.45 }
      ]
    },
    {
      "text": "He shouted and charged forward!",
      "mood": "angry",
      "weight": "high",
      "audio_url": "http://localhost:8000/static/e5f6g7h8.mp3",
      "word_timings": [...]
    }
  ]
}
```

---

## Mood & Voice Matrix

| Mood | Weight | Rate | Pitch | Visual Theme |
|---|---|---|---|---|
| `neutral` | any | +0% | +0Hz | Slate / Grey |
| `hype` | low → high | +5% → +20% | +1Hz → +5Hz | Emerald / Green |
| `tense` | low → high | -5% → -18% | -2Hz → -6Hz | Indigo / Purple |
| `angry` | low → high | +5% → +15% | -2Hz → -6Hz | Rose / Red |
| `sad` | low → high | -5% → -18% | -1Hz → -5Hz | Blue |
| `sarcastic` | low → high | +3% → +8% | +2Hz → +6Hz | Amber / Gold |
| `thoughtful` | low → high | -3% → +5% | -1Hz → -3Hz | Cyan / Teal |

---

## Roadmap

- [ ] Replace edge-tts with OpenAI TTS or ElevenLabs for higher quality voices
- [ ] Add multi-narrator support for dialogue detection
- [ ] Export full audiobook as a single MP3/WAV file
- [ ] Add chapter/section navigation
- [ ] User-configurable mood keyword overrides
- [ ] Persistent project saves with database storage

---

## License

This project is open source and available under the [MIT License](LICENSE).
