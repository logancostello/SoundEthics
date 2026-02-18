import { useState, useRef, useEffect } from "react";
import Navbar from "./components/Navbar";

const dummySongs = {
  "Taylor Swift": ["Shake it Off", "Love Story", "Blank Space"],
  Drake: ["God's Plan", "One Dance", "In My Feelings"],
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

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      handleFiles(e.target.files[0]);
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
    <div
      style={{
        minHeight: "100vh",
        background: "#0a0a0f",
        color: "#e8e0d0",
        fontFamily: "'Courier New', monospace",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Navbar />

      <div style={{ flex: 1, display: "flex" }}>
        {/* LEFT PANEL */}
        <div
          style={{
            width: dividerX,
            borderRight: "1px solid #1e1e2e",
            padding: "28px",
            display: "flex",
            flexDirection: "column",
            gap: "28px",
          }}
        >
          {/* SELECTED TRACKS */}
          {(selectedTracks.length > 0 || uploadedFile) && (
            <div>
              <div
                style={{
                  fontSize: "10px",
                  color: "#555",
                  letterSpacing: "0.12em",
                  marginBottom: "10px",
                  textTransform: "uppercase",
                }}
              >
                Selected Tracks
              </div>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "6px",
                  background: "#111118",
                  padding: "8px",
                  borderRadius: "4px",
                  maxHeight: "140px",
                  overflowY: "auto",
                }}
              >
                {uploadedFile && (
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "4px 8px",
                      borderRadius: "3px",
                      background: "#0f0f16",
                    }}
                  >
                    <span>{uploadedFile.name}</span>
                    <select
                      value={uploadedFile.stem}
                      onChange={(e) =>
                        setUploadedFile({ ...uploadedFile, stem: e.target.value })
                      }
                      style={{
                        background: "#111118",
                        border: "1px solid #2a2a3a",
                        color: "#e8d5b0",
                        cursor: "pointer",
                      }}
                    >
                      <option value="drums">Drums</option>
                      <option value="melody">Melody</option>
                      <option value="chords">Chords</option>
                    </select>
                    <button
                      onClick={() => removeSelectedItem(uploadedFile.name)}
                      style={{
                        border: "none",
                        background: "transparent",
                        color: "#e8d5b0",
                        cursor: "pointer",
                        marginLeft: "6px",
                      }}
                    >
                      ×
                    </button>
                  </div>
                )}

                {selectedTracks.map((track) => (
                  <div
                    key={track.name}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "4px 8px",
                      borderRadius: "3px",
                      background: "#0f0f16",
                    }}
                  >
                    <span>{track.name}</span>
                    <select
                      value={track.stem}
                      onChange={(e) =>
                        updateTrackStem(track.name, e.target.value)
                      }
                      style={{
                        background: "#111118",
                        border: "1px solid #2a2a3a",
                        color: "#e8d5b0",
                        cursor: "pointer",
                      }}
                    >
                      <option value="drums">Drums</option>
                      <option value="melody">Melody</option>
                      <option value="chords">Chords</option>
                    </select>
                    <button
                      onClick={() => removeSelectedItem(track.name)}
                      style={{
                        border: "none",
                        background: "transparent",
                        color: "#e8d5b0",
                        cursor: "pointer",
                        marginLeft: "6px",
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* UPLOAD BOX */}
          <div>
            <div
              style={{
                fontSize: "10px",
                color: "#555",
                letterSpacing: "0.12em",
                marginBottom: "10px",
                textTransform: "uppercase",
              }}
            >
              Upload
            </div>

            <input
              type="file"
              accept="audio/*"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
            />

            <div
              onClick={() => fileInputRef.current.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              style={{
                border: dragActive
                  ? "1px solid #3a3a5a"
                  : "1px dashed #2a2a3a",
                background: dragActive ? "#111122" : "#0f0f16",
                height: "180px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                gap: "14px",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              <svg
                width="36"
                height="36"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#888"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 16V4" />
                <path d="M8 8l4-4 4 4" />
                <path d="M4 20h16" />
              </svg>

              <div
                style={{
                  fontSize: "12px",
                  color: "#888",
                  textAlign: "center",
                }}
              >
                Drag & drop audio file
                <br />
                or click to upload
              </div>
            </div>
          </div>

          {/* SEARCH SONGS */}
          <div>
            <div
              style={{
                fontSize: "10px",
                color: "#555",
                letterSpacing: "0.12em",
                marginBottom: "10px",
                textTransform: "uppercase",
              }}
            >
              Search Songs
            </div>

            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Artist name..."
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "4px",
                border: "1px solid #2a2a3a",
                background: "#111118",
                color: "#e8e0d0",
                fontSize: "13px",
                outline: "none",
              }}
            />

            <div
              style={{
                marginTop: "8px",
                maxHeight: "120px",
                overflowY: "auto",
                border: "1px solid #1e1e2e",
                borderRadius: "4px",
                background: "#0f0f16",
              }}
            >
              {searchResults.map((song) => (
                <div
                  key={song}
                  style={{
                    padding: "8px 12px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span style={{ color: "#aaa" }}>{song}</span>
                  <button
                    onClick={() => toggleTrack(song)}
                    style={{
                      width: "20px",
                      height: "20px",
                      borderRadius: "3px",
                      border: "1px solid #2a2a3a",
                      background: selectedTracks.some((t) => t.name === song)
                        ? "rgba(232,213,176,0.2)"
                        : "transparent",
                      color: "#e8d5b0",
                      cursor: "pointer",
                      fontSize: "12px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {selectedTracks.some((t) => t.name === song) ? "✓" : "+"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* VERTICAL DIVIDER */}
        <div
          onMouseDown={startDraggingX}
          style={{
            width: "1px",
            background: "#2a2a3a",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: "-6px",
              right: "-6px",
              top: 0,
              bottom: 0,
              cursor: "col-resize",
            }}
          />
        </div>

        {/* RIGHT PANEL */}
        <div
          ref={rightPanelRef}
          style={{ flex: 1, display: "flex", flexDirection: "column" }}
        >
          {/* TOP RIGHT */}
          <div
            style={{
              height: dividerY,
              padding: "28px",
              borderBottom: "1px solid #1e1e2e",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
            }}
          >
            <div
              style={{
                fontSize: "10px",
                color: "#555",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
              }}
            >
              Prompt
            </div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the beat you want..."
              style={{
                flex: 1,
                resize: "none",
                background: "#111118",
                border: "1px solid #1e1e2e",
                color: "#e8e0d0",
                padding: "12px",
                fontSize: "14px",
                outline: "none",
              }}
            />

            <button
              onClick={handleGenerate}
              style={{
                alignSelf: "flex-start",
                padding: "8px 18px",
                background: "#1e1e2e",
                border: "1px solid #2a2a3a",
                color: "#e8d5b0",
                fontSize: "12px",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                cursor: "pointer",
              }}
            >
              Generate
            </button>
          </div>

          {/* HORIZONTAL DIVIDER */}
          <div
            onMouseDown={startDraggingY}
            style={{
              height: "1px",
              background: "#2a2a3a",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "-6px",
                bottom: "-6px",
                left: 0,
                right: 0,
                cursor: "row-resize",
              }}
            />
          </div>

          {/* BOTTOM RIGHT */}
          <div style={{ flex: 1, padding: "28px" }} />
        </div>
      </div>
    </div>
  );
}

export default App;
