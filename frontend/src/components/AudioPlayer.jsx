import { useState, useRef, useEffect } from "react";

/*
  AudioPlayer
  props:
    - src: string (blob URL or file URL)
    - filename: string (used for download)
*/
export default function AudioPlayer({ src, filename }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onLoadedMetadata = () => setDuration(audio.duration);
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", onTimeUpdate);
    audio.addEventListener("loadedmetadata", onLoadedMetadata);
    audio.addEventListener("ended", onEnded);

    return () => {
      audio.removeEventListener("timeupdate", onTimeUpdate);
      audio.removeEventListener("loadedmetadata", onLoadedMetadata);
      audio.removeEventListener("ended", onEnded);
    };
  }, [src]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const audio = audioRef.current;
    if (!audio) return;
    const val = parseFloat(e.target.value);
    audio.currentTime = val;
    setCurrentTime(val);
  };

  const handleVolume = (e) => {
    const audio = audioRef.current;
    if (!audio) return;
    const val = parseFloat(e.target.value);
    audio.volume = val;
    setVolume(val);
  };

  const formatTime = (t) => {
    if (isNaN(t)) return "0:00";
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  return (
    <div style={styles.wrapper}>
      <audio ref={audioRef} src={src} preload="metadata" />

      {/* Play / Pause */}
      <button onClick={togglePlay} style={styles.playBtn}>
        {isPlaying ? (
          /* Pause icon */
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="2" y="1" width="4" height="12" fill="currentColor" />
            <rect x="8" y="1" width="4" height="12" fill="currentColor" />
          </svg>
        ) : (
          /* Play icon */
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <polygon points="2,1 13,7 2,13" fill="currentColor" />
          </svg>
        )}
      </button>

      {/* Seek bar */}
      <span style={styles.time}>{formatTime(currentTime)}</span>
      <input
        type="range"
        min={0}
        max={duration || 0}
        step={0.01}
        value={currentTime}
        onChange={handleSeek}
        style={{ ...styles.slider, flex: 1 }}
      />
      <span style={styles.time}>{formatTime(duration)}</span>

      {/* Volume */}
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{ flexShrink: 0, color: "var(--color-text-muted)" }}>
        <polygon points="1,4 5,4 9,1 9,13 5,10 1,10" fill="currentColor" />
        {volume > 0 && <path d="M10.5 4.5 C12 5.5 12 8.5 10.5 9.5" stroke="currentColor" strokeWidth="1.2" fill="none" />}
        {volume > 0.5 && <path d="M11.5 2.5 C14 4 14 10 11.5 11.5" stroke="currentColor" strokeWidth="1.2" fill="none" />}
      </svg>
      <input
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={volume}
        onChange={handleVolume}
        style={{ ...styles.slider, width: 60 }}
      />

      {/* Download */}
      <a href={src} download={filename} style={styles.downloadBtn} title="Download">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M7 1 L7 9 M4 6.5 L7 9.5 L10 6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M1 11 L1 13 L13 13 L13 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </a>
    </div>
  );
}

const styles = {
  wrapper: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    background: "var(--color-bg-panel)",
    border: "1px solid var(--icon-btn-border)",
    padding: "10px 14px",
    width: "100%",
    boxSizing: "border-box",
  },
  playBtn: {
    width: 28,
    height: 28,
    flexShrink: 0,
    background: "transparent",
    border: "1px solid var(--icon-btn-border)",
    color: "var(--color-text)",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 0,
  },
  time: {
    fontSize: "var(--font-size-xs)",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-primary)",
    flexShrink: 0,
    minWidth: 32,
    textAlign: "center",
  },
  slider: {
    appearance: "none",
    WebkitAppearance: "none",
    height: 2,
    background: "var(--icon-btn-border)",
    outline: "none",
    cursor: "pointer",
    accentColor: "var(--color-accent)",
    flexShrink: 0,
  },
  downloadBtn: {
    flexShrink: 0,
    width: 28,
    height: 28,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    border: "1px solid var(--icon-btn-border)",
    color: "var(--color-text)",
    textDecoration: "none",
    cursor: "pointer",
  },
};