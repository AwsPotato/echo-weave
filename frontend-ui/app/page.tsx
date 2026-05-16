"use client";

import { useState, useRef, useEffect } from "react";
import { Loader2, Play, AudioLines, Sparkles } from "lucide-react";

interface ProcessTextChunk {
  original_text: string;
  mood: string;
  audio_url: string;
}

interface ProcessTextResponse {
  chunks: ProcessTextChunk[];
}

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [chunks, setChunks] = useState<ProcessTextChunk[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Single audio element ref for playing
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingUrl, setPlayingUrl] = useState<string | null>(null);

  // Stop playing when component unmounts
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
      }
    };
  }, []);

  const handleGenerate = async () => {
    if (!text.trim()) return;
    
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

  const handlePlayAudio = (url: string) => {
    if (!audioRef.current) return;
    
    // If playing the same URL, pause it
    if (playingUrl === url && !audioRef.current.paused) {
      audioRef.current.pause();
      setPlayingUrl(null);
      return;
    }

    // Otherwise load and play the new URL
    audioRef.current.src = url;
    audioRef.current.play().catch(e => console.error("Playback failed", e));
    setPlayingUrl(url);
  };

  const getMoodStyles = (mood: string) => {
    switch (mood) {
      case "ominous_suspense":
        return "border-indigo-500/50 bg-indigo-950/20 text-indigo-100 shadow-[0_0_15px_rgba(99,102,241,0.1)] hover:border-indigo-400";
      case "high_action":
        return "border-rose-500/50 bg-rose-950/20 text-rose-100 shadow-[0_0_15px_rgba(244,63,94,0.1)] hover:border-rose-400";
      case "analytical_inner":
        return "border-cyan-500/50 bg-cyan-950/20 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.1)] hover:border-cyan-400";
      case "awe_astonishment":
        return "border-amber-500/50 bg-amber-950/20 text-amber-100 shadow-[0_0_15px_rgba(245,158,11,0.1)] hover:border-amber-400";
      case "grim_savage":
        return "border-orange-700/50 bg-orange-950/30 text-orange-100 shadow-[0_0_15px_rgba(194,65,12,0.1)] hover:border-orange-500";
      case "neutral_narrative":
      default:
        return "border-slate-700 bg-slate-800/50 text-slate-200 hover:border-slate-500";
    }
  };

  const getMoodBadge = (mood: string) => {
    switch (mood) {
      case "ominous_suspense":
        return "bg-indigo-900/50 text-indigo-300 border-indigo-700/50";
      case "high_action":
        return "bg-rose-900/50 text-rose-300 border-rose-700/50";
      case "analytical_inner":
        return "bg-cyan-900/50 text-cyan-300 border-cyan-700/50";
      case "awe_astonishment":
        return "bg-amber-900/50 text-amber-300 border-amber-700/50";
      case "grim_savage":
        return "bg-orange-900/50 text-orange-300 border-orange-700/50";
      case "neutral_narrative":
      default:
        return "bg-slate-700/50 text-slate-300 border-slate-600";
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 font-sans selection:bg-indigo-500/30">
      <audio ref={audioRef} onEnded={() => setPlayingUrl(null)} />
      
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
            <div className="flex items-center gap-4 px-2">
              <h2 className="text-2xl font-bold text-white tracking-tight">Timeline</h2>
              <div className="h-px bg-slate-800 flex-1" />
              <span className="text-sm text-slate-500 font-medium px-3 py-1 bg-slate-900 rounded-full border border-slate-800">
                {chunks.length} chunks generated
              </span>
            </div>

            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-800 before:to-transparent">
              {chunks.map((chunk, index) => {
                const isPlaying = playingUrl === chunk.audio_url;
                return (
                  <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    {/* Timeline Dot */}
                    <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-slate-950 bg-slate-800 z-10 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm text-slate-500 text-sm font-bold">
                      {index + 1}
                    </div>
                    
                    {/* Card */}
                    <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] p-5 rounded-2xl border transition-all duration-300 backdrop-blur-sm relative group-hover:-translate-y-1 ${getMoodStyles(chunk.mood)}`}>
                      <div className="flex flex-col h-full gap-4">
                        <div className="flex items-start justify-between gap-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getMoodBadge(chunk.mood)} uppercase tracking-wider`}>
                            {chunk.mood}
                          </span>
                          <button
                            onClick={() => handlePlayAudio(chunk.audio_url)}
                            className={`p-2 rounded-full transition-all shrink-0 border ${
                              isPlaying 
                                ? "bg-indigo-500 text-white border-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.4)]" 
                                : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white"
                            }`}
                            aria-label="Play audio"
                          >
                            {isPlaying ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Play className="w-4 h-4 ml-0.5" />
                            )}
                          </button>
                        </div>
                        <p className="text-base leading-relaxed opacity-90 text-pretty">
                          {chunk.original_text}
                        </p>
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
