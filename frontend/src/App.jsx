import { useState, useRef, useEffect } from "react";
import Navbar from "./components/Navbar";
import AudioPlayer from "./components/AudioPlayer";
import { handleGenerate } from "./services/generateService";
import "./App.css";

const dummySongs = {
  "Taylor Swift": ["Shake it Off", "Love Story", "Blank Space"],
  "Drake": ["God's Plan", "One Dance", "In My Feelings"],
  "Kendrick Lamar": ["HUMBLE.", "DNA.", "Alright"],
};

function songSearch(input) { 
  const keys = [];
  const songs = [];
  
  input = input.toLowerCase();

  for (const key in dummySongs) {
    if (key.toLowerCase().includes(input)) { keys.push.apply(keys, dummySongs[key]); }
    else {
      for (const song of dummySongs[key]) {
        if (song.toLowerCase().includes(input)) { songs.push(song); } 
      }
    }
  }

  return keys.concat(songs);
}

function App() {
  const [dividerX, setDividerX] = useState(window.innerWidth / 2);
  const [dividerY, setDividerY] = useState(window.innerHeight / 2);
  const [prompt, setPrompt] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTracks, setSelectedTracks] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [stemResult, setStemResult] = useState(null); // { audioUrl, filename }

  const draggingX = useRef(false);
  const draggingY = useRef(false);
  const rightPanelRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (draggingX.current) {
        const min = 250;
        const max = window.innerWidth - 250;
        setDividerX(Math.max(min, Math.min(max, e.clientX)));
      }
      if (draggingY.current && rightPanelRef.current) {
        const rect = rightPanelRef.current.getBoundingClientRect();
        const relativeY = e.clientY - rect.top;
        const min = 150;
        const max = rect.height - 150;
        setDividerY(Math.max(min, Math.min(max, relativeY)));
      }
    };

    const handleMouseUp = () => {
      draggingX.current = false;
      draggingY.current = false;
      document.body.style.cursor = "default";
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  const startDraggingX = () => {
    draggingX.current = true;
    document.body.style.cursor = "col-resize";
  };

  const startDraggingY = () => {
    draggingY.current = true;
    document.body.style.cursor = "row-resize";
  };

  const onGenerate = () => {
    setStemResult(null);
    handleGenerate(selectedTracks, {
      onError: setError,
      onSuccess: (audioUrl, filename) => setStemResult({ audioUrl, filename }),
      onLoading: setIsLoading,
    });
  };

  const handleFiles = (files) => {
    const newTracks = Array.from(files)
      .filter(f => !selectedTracks.some(t => t.name === f.name))
      .map(f => ({ name: f.name, stem: "vocals", file: f }));
    setSelectedTracks(prev => [...prev, ...newTracks]);
  };

  const toggleTrack = (trackName) => {
    setSelectedTracks((prev) => {
      const exists = prev.find((t) => t.name === trackName);
      if (exists) return prev.filter((t) => t.name !== trackName);
      return [...prev, { name: trackName, stem: "vocals" }];
    });
  };

  const removeSelectedItem = (name) => {
    setSelectedTracks((prev) => prev.filter((t) => t.name !== name));
  };

  const updateTrackStem = (name, stem) => {
    setSelectedTracks((prev) =>
      prev.map((t) => (t.name === name ? { ...t, stem } : t))
    );
  };

  const searchResults = songSearch(searchQuery) || [];
  const hasSelections = selectedTracks.length > 0;

  return (
    <div className="app">
      <Navbar />

      <div className="main">
        {/* LEFT PANEL */}
        <div className="left-panel" style={{ width: dividerX, display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>

          {/* Selected Tracks */}
          <div style={{ flexShrink: 0 }}>
            <div className="section-label">Selected Tracks</div>

            <div className="selected-container">
              {!hasSelections ? (
                <span style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-small)", padding: "4px 8px" }}>
                  No tracks selected
                </span>
              ) : (
                selectedTracks.map((track) => (
                  <div key={track.name} className="selected-item">
                    <span>{track.name}</span>
                    <select
                      value={track.stem}
                      onChange={(e) => updateTrackStem(track.name, e.target.value)}
                      className="stem-select"
                    >
                      <option value="vocals">Vocals</option>
                      <option value="drums">Drums</option>
                      <option value="bass">Bass</option>
                      <option value="other">Other</option>
                    </select>
                    <button
                      onClick={() => removeSelectedItem(track.name)}
                      className="remove-btn"
                    >
                      ×
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Upload */}
          <div style={{ flexShrink: 0 }}>
            <div className="section-label">Upload</div>

            <input
              type="file"
              accept="audio/*"
              multiple
              ref={fileInputRef}
              onChange={(e) => e.target.files.length && handleFiles(e.target.files)}
              hidden
            />

            <div
              className={`upload-box ${dragActive ? "drag-active" : ""}`}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="upload-text">
                Drag and drop audio file
                <br />
                or click to upload
              </div>
            </div>
          </div>

          {/* Search */}
          <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
            <div className="section-label">Search Songs</div>

            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search"
              className="search-input"
            />

            <div className="search-results" style={{ flex: 1, overflowY: "auto", minHeight: 0, maxHeight: "none" }}>
              {searchResults.map((song) => {
                const isSelected = selectedTracks.some((t) => t.name === song);
                return (
                  <div key={song} className="search-item">
                    <span className="song-name">{song}</span>
                    <button
                      onClick={() => toggleTrack(song)}
                      className={`add-btn ${isSelected ? "active" : ""}`}
                    >
                      {isSelected ? "✓" : "+"}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Vertical Divider */}
        <div className="vertical-divider" onMouseDown={startDraggingX}>
          <div className="divider-hitbox-x" />
        </div>

        {/* RIGHT PANEL */}
        <div className="right-panel" ref={rightPanelRef}>
          <div className="top-right" style={{ height: dividerY }}>
            <div className="section-label" style={{ marginBottom: 0 }}>Prompt</div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the song you want..."
              className="prompt-textarea"
            />

            <button onClick={onGenerate} className="generate-btn" disabled={isLoading}>
              {isLoading ? "Generating..." : "Generate"}
            </button>

            {error && (
              <p style={{ color: "#ff6b6b", fontSize: "var(--font-size-small)", margin: 0 }}>
                {error}
              </p>
            )}
          </div>

          <div className="horizontal-divider" onMouseDown={startDraggingY}>
            <div className="divider-hitbox-y" />
          </div>

          {/* BOTTOM RIGHT */}
          <div className="bottom-right">
            <div className="section-label">Generated Output</div>

            {isLoading && (
              <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-small)" }}>
                Splitting stems, this may take a minute...
              </p>
            )}

            {stemResult && !isLoading && (
              <AudioPlayer src={stemResult.audioUrl} filename={stemResult.filename} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;