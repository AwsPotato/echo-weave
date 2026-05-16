"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Loader2, Play, Pause, Square, AudioLines, Sparkles, Crosshair } from "lucide-react";

interface WordTiming {
  word: string;
  offset: number;
  duration: number;
}

interface ProcessTextChunk {
  text: string;
  mood: string;
  weight: string;
  audio_url: string;
  word_timings: WordTiming[];
}

interface ProcessTextResponse {
  chunks: ProcessTextChunk[];
}

const SPEED_OPTIONS = [0.5, 0.75, 1, 1.25, 1.5, 2];

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [chunks, setChunks] = useState<ProcessTextChunk[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Audio state
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingUrl, setPlayingUrl] = useState<string | null>(null);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  // Sequential playback state
  const [isPlayingAll, setIsPlayingAll] = useState(false);
  const [currentChunkIndex, setCurrentChunkIndex] = useState<number>(-1);
  const isPlayingAllRef = useRef(false);

  // Word highlight state
  const [activeWordIndex, setActiveWordIndex] = useState<number>(-1);
  const animFrameRef = useRef<number | null>(null);

  // Auto-scroll setting
  const [autoScroll, setAutoScroll] = useState(false);
  const activeWordRef = useRef<HTMLSpanElement | null>(null);
  const activeCardRef = useRef<HTMLDivElement | null>(null);

  // Apply playback speed whenever it changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  // Stop playing when component unmounts
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
      }
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, []);

  // Auto-scroll to active word or card
  useEffect(() => {
    if (!autoScroll) return;
    if (activeWordRef.current) {
      activeWordRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    } else if (activeCardRef.current) {
      activeCardRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeWordIndex, currentChunkIndex, autoScroll]);

  // Word tracking via requestAnimationFrame for smooth highlights
  useEffect(() => {
    const trackWords = () => {
      const audio = audioRef.current;
      if (!audio || audio.paused || !playingUrl) {
        animFrameRef.current = requestAnimationFrame(trackWords);
        return;
      }

      const currentTime = audio.currentTime;
      const playingChunk = chunks.find(c => c.audio_url === playingUrl);

      if (!playingChunk || playingChunk.word_timings.length === 0) {
        setActiveWordIndex(-1);
        animFrameRef.current = requestAnimationFrame(trackWords);
        return;
      }

      const timings = playingChunk.word_timings;
      let wordIdx = -1;
      for (let i = timings.length - 1; i >= 0; i--) {
        if (currentTime >= timings[i].offset) {
          wordIdx = i;
          break;
        }
      }

      setActiveWordIndex(wordIdx);
      animFrameRef.current = requestAnimationFrame(trackWords);
    };

    animFrameRef.current = requestAnimationFrame(trackWords);
    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [playingUrl, chunks]);

  // Reset active word when playingUrl changes
  useEffect(() => {
    setActiveWordIndex(-1);
  }, [playingUrl]);

  // Sequential playback: when a chunk finishes, advance to next
  const handleAudioEnded = useCallback(() => {
    if (isPlayingAllRef.current && currentChunkIndex >= 0) {
      const nextIndex = currentChunkIndex + 1;
      if (nextIndex < chunks.length) {
        setCurrentChunkIndex(nextIndex);
        const nextChunk = chunks[nextIndex];
        setPlayingUrl(nextChunk.audio_url);
        if (audioRef.current) {
          audioRef.current.src = nextChunk.audio_url;
          audioRef.current.playbackRate = playbackSpeed;
          audioRef.current.play().catch(e => console.error("Playback failed", e));
        }
      } else {
        stopPlayAll();
      }
    } else {
      setPlayingUrl(null);
    }
  }, [currentChunkIndex, chunks, playbackSpeed]);

  // Attach the onEnded handler
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.onended = handleAudioEnded;
    return () => { audio.onended = null; };
  }, [handleAudioEnded]);

  const handleGenerate = async () => {
    if (!text.trim()) return;
    
    stopPlayAll();
    setLoading(true);
    setError(null);
    setChunks([]);
    setPlayingUrl(null);

    try {
      const response = await fetch("http://localhost:8000/api/process-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: ProcessTextResponse = await response.json();
      setChunks(data.chunks);
    } catch (err: any) {
      setError(err.message || "Failed to process text.");
    } finally {
      setLoading(false);
    }
  };

  // Play from a specific chunk index and continue sequentially
  const playFromChunk = (startIndex: number) => {
    if (chunks.length === 0 || !audioRef.current || startIndex < 0 || startIndex >= chunks.length) return;

    // If already playing the same chunk, toggle pause/resume
    if (isPlayingAll && currentChunkIndex === startIndex && playingUrl === chunks[startIndex].audio_url) {
      if (audioRef.current.paused) {
        audioRef.current.play().catch(e => console.error("Playback failed", e));
      } else {
        audioRef.current.pause();
      }
      return;
    }

    isPlayingAllRef.current = true;
    setIsPlayingAll(true);
    setCurrentChunkIndex(startIndex);

    const chunk = chunks[startIndex];
    setPlayingUrl(chunk.audio_url);
    audioRef.current.src = chunk.audio_url;
    audioRef.current.playbackRate = playbackSpeed;
    audioRef.current.play().catch(e => console.error("Playback failed", e));
  };

  const handlePlayAll = () => {
    if (chunks.length === 0 || !audioRef.current) return;

    if (isPlayingAll) {
      if (audioRef.current.paused) {
        audioRef.current.play().catch(e => console.error("Playback failed", e));
      } else {
        audioRef.current.pause();
      }
      return;
    }

    playFromChunk(0);
  };

  const stopPlayAll = () => {
    isPlayingAllRef.current = false;
    setIsPlayingAll(false);
    setCurrentChunkIndex(-1);
    setPlayingUrl(null);
    setActiveWordIndex(-1);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
    }
  };

  const getMoodStyles = (mood: string) => {
    switch (mood) {
      case "hype":
        return "border-emerald-500/50 bg-emerald-950/20 text-emerald-100 shadow-[0_0_15px_rgba(16,185,129,0.1)] hover:border-emerald-400";
      case "tense":
        return "border-indigo-500/50 bg-indigo-950/20 text-indigo-100 shadow-[0_0_15px_rgba(99,102,241,0.1)] hover:border-indigo-400";
      case "angry":
        return "border-rose-500/50 bg-rose-950/20 text-rose-100 shadow-[0_0_15px_rgba(244,63,94,0.1)] hover:border-rose-400";
      case "sad":
        return "border-blue-500/50 bg-blue-950/20 text-blue-100 shadow-[0_0_15px_rgba(59,130,246,0.1)] hover:border-blue-400";
      case "sarcastic":
        return "border-amber-500/50 bg-amber-950/20 text-amber-100 shadow-[0_0_15px_rgba(245,158,11,0.1)] hover:border-amber-400";
      case "thoughtful":
        return "border-cyan-500/50 bg-cyan-950/20 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.1)] hover:border-cyan-400";
      case "neutral":
      default:
        return "border-slate-700 bg-slate-800/50 text-slate-200 hover:border-slate-500";
    }
  };

  const getMoodBadge = (mood: string) => {
    switch (mood) {
      case "hype":
        return "bg-emerald-900/50 text-emerald-300 border-emerald-700/50";
      case "tense":
        return "bg-indigo-900/50 text-indigo-300 border-indigo-700/50";
      case "angry":
        return "bg-rose-900/50 text-rose-300 border-rose-700/50";
      case "sad":
        return "bg-blue-900/50 text-blue-300 border-blue-700/50";
      case "sarcastic":
        return "bg-amber-900/50 text-amber-300 border-amber-700/50";
      case "thoughtful":
        return "bg-cyan-900/50 text-cyan-300 border-cyan-700/50";
      case "neutral":
      default:
        return "bg-slate-700/50 text-slate-300 border-slate-600";
    }
  };

  const getWeightBadge = (weight: string) => {
    switch (weight) {
      case "high":
        return "bg-red-900/40 text-red-300 border-red-700/50";
      case "medium":
        return "bg-yellow-900/40 text-yellow-300 border-yellow-700/50";
      case "low":
      default:
        return "bg-slate-800/40 text-slate-400 border-slate-700/50";
    }
  };

  const renderChunkText = (chunk: ProcessTextChunk) => {
    const isActiveChunk = playingUrl === chunk.audio_url;

    if (!isActiveChunk || chunk.word_timings.length === 0) {
      return (
        <p className="text-base leading-relaxed opacity-90 text-pretty">
          {chunk.text}
        </p>
      );
    }

    return (
      <p className="text-base leading-relaxed text-pretty">
        {chunk.word_timings.map((wt, i) => (
          <span
            key={i}
            ref={i === activeWordIndex ? activeWordRef : undefined}
            className={`transition-all duration-150 rounded-sm ${
              i === activeWordIndex
                ? "bg-indigo-500/40 text-white px-0.5 -mx-0.5 py-0.5"
                : i < activeWordIndex
                ? "opacity-60"
                : "opacity-90"
            }`}
          >
            {wt.word}{" "}
          </span>
        ))}
      </p>
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 font-sans selection:bg-indigo-500/30">
      <audio ref={audioRef} />
      
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header */}
        <header className="space-y-4 text-center md:text-left">
          <div className="inline-flex items-center justify-center space-x-3 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-800 mb-2">
            <AudioLines className="w-5 h-5 text-indigo-400" />
            <span className="text-sm font-medium tracking-wide text-slate-300">Echo-Weave</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent">
            Smart Audio Pipeline
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto md:mx-0">
            Transform text into adaptive audio experiences. We analyze mood and context to generate the perfect voice parameters.
          </p>
        </header>

        {/* Input Section */}
        <section className="space-y-6 bg-slate-900/30 p-1 rounded-3xl border border-slate-800/50 backdrop-blur-sm">
          <div className="p-6 md:p-8 space-y-6">
            <div className="space-y-2">
              <label htmlFor="script" className="block text-sm font-medium text-slate-400 ml-1">
                Story Script or Chapter
              </label>
              <textarea
                id="script"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your story here... The system will chunk it and adapt the voice to the context."
                className="w-full h-64 p-5 bg-slate-900/80 border border-slate-800 rounded-2xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all resize-none text-slate-200 placeholder:text-slate-600 text-lg leading-relaxed shadow-inner"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm text-slate-500">
                {text.length} characters
              </div>
              <button
                onClick={handleGenerate}
                disabled={loading || !text.trim()}
                className="group relative inline-flex items-center justify-center px-8 py-3.5 text-base font-medium text-white transition-all duration-200 bg-indigo-600 border border-transparent rounded-xl hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden shadow-lg shadow-indigo-500/25"
              >
                <div className="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-black" />
                <span className="relative flex items-center gap-2">
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 group-hover:text-indigo-200 transition-colors" />
                      Generate Adaptive Audio
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {error && (
              <div className="p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-red-400 text-sm flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                {error}
              </div>
            )}
          </div>
        </section>

        {/* Timeline Section */}
        {chunks.length > 0 && (
          <section className="space-y-6 pt-4 animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* Playback Controls Bar */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-2">
              <div className="flex items-center gap-4">
                <h2 className="text-2xl font-bold text-white tracking-tight">Timeline</h2>
                <div className="h-px bg-slate-800 w-8" />
                <span className="text-sm text-slate-500 font-medium px-3 py-1 bg-slate-900 rounded-full border border-slate-800">
                  {chunks.length} chunks
                </span>
              </div>

              <div className="flex items-center gap-3">
                {/* Auto-scroll toggle */}
                <button
                  onClick={() => setAutoScroll(!autoScroll)}
                  title={autoScroll ? "Auto-scroll ON" : "Auto-scroll OFF"}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all border ${
                    autoScroll
                      ? "bg-indigo-600/20 text-indigo-300 border-indigo-700/50"
                      : "bg-slate-900/80 text-slate-500 border-slate-800 hover:text-slate-300"
                  }`}
                >
                  <Crosshair className="w-3.5 h-3.5" />
                  Follow
                </button>

                {/* Speed Selector */}
                <div className="flex items-center gap-1.5 bg-slate-900/80 border border-slate-800 rounded-xl px-3 py-1.5">
                  <span className="text-xs text-slate-500 font-medium mr-1">Speed</span>
                  {SPEED_OPTIONS.map((speed) => (
                    <button
                      key={speed}
                      onClick={() => setPlaybackSpeed(speed)}
                      className={`px-2 py-0.5 rounded-lg text-xs font-semibold transition-all ${
                        playbackSpeed === speed
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-white hover:bg-slate-800"
                      }`}
                    >
                      {speed}x
                    </button>
                  ))}
                </div>

                {/* Play All / Stop */}
                <button
                  onClick={isPlayingAll ? stopPlayAll : handlePlayAll}
                  className={`inline-flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-medium transition-all border ${
                    isPlayingAll
                      ? "bg-rose-600/20 text-rose-300 border-rose-700/50 hover:bg-rose-600/30"
                      : "bg-emerald-600/20 text-emerald-300 border-emerald-700/50 hover:bg-emerald-600/30"
                  }`}
                >
                  {isPlayingAll ? (
                    <>
                      <Square className="w-4 h-4" />
                      Stop
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Play All
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Progress indicator during play-all */}
            {isPlayingAll && currentChunkIndex >= 0 && (
              <div className="px-2">
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${((currentChunkIndex + 1) / chunks.length) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1.5">
                  Playing chunk {currentChunkIndex + 1} of {chunks.length}
                </p>
              </div>
            )}

            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-800 before:to-transparent">
              {chunks.map((chunk, index) => {
                const isPlaying = playingUrl === chunk.audio_url;
                const isCurrentInPlayAll = isPlayingAll && currentChunkIndex === index;
                return (
                  <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    {/* Timeline Dot — click to play from this chunk */}
                    <button
                      onClick={() => playFromChunk(index)}
                      className={`flex items-center justify-center w-12 h-12 rounded-full border-4 border-slate-950 z-10 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm text-sm font-bold transition-all cursor-pointer hover:scale-110 ${
                        isCurrentInPlayAll
                          ? "bg-indigo-600 text-white border-indigo-500/50 shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                          : "bg-slate-800 text-slate-500 hover:bg-slate-700 hover:text-white"
                      }`}
                      aria-label={`Play from chunk ${index + 1}`}
                    >
                      {index + 1}
                    </button>
                    
                    {/* Card */}
                    <div
                      ref={isCurrentInPlayAll ? activeCardRef : undefined}
                      className={`w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] p-5 rounded-2xl border transition-all duration-300 backdrop-blur-sm relative group-hover:-translate-y-1 ${getMoodStyles(chunk.mood)} ${isCurrentInPlayAll ? "ring-2 ring-indigo-500/40" : ""}`}
                    >
                      <div className="flex flex-col h-full gap-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getMoodBadge(chunk.mood)} uppercase tracking-wider`}>
                              {chunk.mood}
                            </span>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold border ${getWeightBadge(chunk.weight)} uppercase tracking-widest`}>
                              {chunk.weight}
                            </span>
                          </div>
                          <button
                            onClick={() => playFromChunk(index)}
                            className={`p-2 rounded-full transition-all shrink-0 border ${
                              isPlaying 
                                ? "bg-indigo-500 text-white border-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.4)]" 
                                : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white"
                            }`}
                            aria-label="Play from here"
                          >
                            {isPlaying ? (
                              <Pause className="w-4 h-4" />
                            ) : (
                              <Play className="w-4 h-4 ml-0.5" />
                            )}
                          </button>
                        </div>
                        {renderChunkText(chunk)}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
