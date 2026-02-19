import { useState, useRef, useEffect } from "react";
import Navbar from "./components/Navbar";
import "./App.css";

const dummySongs = {
  "Taylor Swift": ["Shake it Off", "Love Story", "Blank Space"],
  "Drake": ["God's Plan", "One Dance", "In My Feelings"],
  "Kendrick Lamar": ["HUMBLE.", "DNA.", "Alright"],
};

function App() {
  const [dividerX, setDividerX] = useState(window.innerWidth / 2);
  const [dividerY, setDividerY] = useState(window.innerHeight / 2);
  const [prompt, setPrompt] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState("Taylor Swift");
  const [selectedTracks, setSelectedTracks] = useState([]);

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

  const handleGenerate = () => {
    console.log("Generating with prompt:", prompt);
    console.log("Selected Tracks:", selectedTracks);
  };

  const handleFiles = (file) => {
    if (file) {
      setUploadedFile({ name: file.name, stem: "melody" });
    }
  };

  const toggleTrack = (trackName) => {
    setSelectedTracks((prev) => {
      const exists = prev.find((t) => t.name === trackName);
      if (exists) return prev.filter((t) => t.name !== trackName);
      return [...prev, { name: trackName, stem: "melody" }];
    });
  };

  const removeSelectedItem = (name) => {
    if (uploadedFile?.name === name) setUploadedFile(null);
    else setSelectedTracks((prev) => prev.filter((t) => t.name !== name));
  };

  const updateTrackStem = (name, stem) => {
    setSelectedTracks((prev) =>
      prev.map((t) => (t.name === name ? { ...t, stem } : t))
    );
    if (uploadedFile?.name === name) setUploadedFile({ ...uploadedFile, stem });
  };

  const searchResults = dummySongs[searchQuery] || [];

  return (
    <div className="app">
      <Navbar />

      <div className="main">
        {/* LEFT PANEL */}
        <div className="left-panel" style={{ width: dividerX }}>
          
          {(selectedTracks.length > 0 || uploadedFile) && (
            <div>
              <div className="section-label">Selected Tracks</div>

              <div className="selected-container">
                {uploadedFile && (
                  <div className="selected-item">
                    <span>{uploadedFile.name}</span>
                    <select
                      value={uploadedFile.stem}
                      onChange={(e) =>
                        setUploadedFile({ ...uploadedFile, stem: e.target.value })
                      }
                      className="stem-select"
                    >
                      <option value="drums">Drums</option>
                      <option value="melody">Melody</option>
                      <option value="chords">Chords</option>
                    </select>
                    <button
                      onClick={() => removeSelectedItem(uploadedFile.name)}
                      className="remove-btn"
                    >
                      ×
                    </button>
                  </div>
                )}

                {selectedTracks.map((track) => (
                  <div key={track.name} className="selected-item">
                    <span>{track.name}</span>
                    <select
                      value={track.stem}
                      onChange={(e) =>
                        updateTrackStem(track.name, e.target.value)
                      }
                      className="stem-select"
                    >
                      <option value="drums">Drums</option>
                      <option value="melody">Melody</option>
                      <option value="chords">Chords</option>
                    </select>
                    <button
                      onClick={() => removeSelectedItem(track.name)}
                      className="remove-btn"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload */}
          <div>
            <div className="section-label">Upload</div>

            <input
              type="file"
              accept="audio/*"
              ref={fileInputRef}
              onChange={(e) => e.target.files[0] && handleFiles(e.target.files[0])}
              hidden
            />

            <div
              className={`upload-box ${dragActive ? "drag-active" : ""}`}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="upload-text">
                Drag & drop audio file
                <br />
                or click to upload
              </div>
            </div>
          </div>

          {/* Search */}
          <div>
            <div className="section-label">Search Songs</div>

            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Artist name..."
              className="search-input"
            />

            <div className="search-results">
              {searchResults.map((song) => {
                const isSelected = selectedTracks.some(
                  (t) => t.name === song
                );
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
          <div
            className="top-right"
            style={{ height: dividerY }}
          >
            <div className="section-label">Prompt</div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the beat you want..."
              className="prompt-textarea"
            />

            <button onClick={handleGenerate} className="generate-btn">
              Generate
            </button>
          </div>

          <div className="horizontal-divider" onMouseDown={startDraggingY}>
            <div className="divider-hitbox-y" />
          </div>

          <div className="bottom-right" />
        </div>
      </div>
    </div>
  );
}

export default App;
