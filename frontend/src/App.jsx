import { useState, useRef, useEffect } from "react";
import Navbar from "./components/Navbar";
import AudioPlayer from "./components/AudioPlayer";
import AttributionTable from "./components/AttributionTable";
import NumberInput from "./components/NumberInput";
import DropdownInput from "./components/DropdownInput";
import BooleanInput from "./components/BooleanInput";
import { handleGenerate } from "./services/generateService";
import "./App.css";

function App() {
  const [dividerX, setDividerX] = useState(window.innerWidth / 2);
  const [dividerY, setDividerY] = useState(window.innerHeight * 0.35);
  const [prompt, setPrompt] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [selectedTracks, setSelectedTracks] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [stemResult, setStemResult] = useState(null);
  const [bpm, setBpm] = useState(null);
  const [duration, setDuration] = useState(null);
  const [inferenceSteps, setInferenceSteps] = useState(null);
  const [seed, setSeed] = useState(null);
  const [isThinking, setThinking] = useState(true);
  const [coverStrength, setCoverStrength] = useState(null);
  const [guidanceScale, setGuidanceScale] = useState(null);
   const [key, setKey] = useState("");

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
    const tracksSnapshot = selectedTracks.map(t => ({ name: t.name, stem: t.stem }));

    // TODO: here is the call to generation, so would need to add a parameter here
    handleGenerate(selectedTracks, prompt, { bpm, duration, inferenceSteps, seed, isThinking, coverStrength, guidanceScale, key }, {
      onError: setError,
      onSuccess: (audioUrl, filename) =>
        setStemResult({ audioUrl, filename, tracks: tracksSnapshot }),
      onLoading: setIsLoading,
    });
  };

  const handleFiles = (files) => {
    const newTracks = Array.from(files)
      .filter(f => !selectedTracks.some(t => t.name === f.name))
      .map(f => ({ name: f.name, stem: "drums", file: f }));
    setSelectedTracks(prev => [...prev, ...newTracks]);
  };

  const removeSelectedItem = (name) => {
    setSelectedTracks((prev) => prev.filter((t) => t.name !== name));
  };

  const updateTrackStem = (name, stem) => {
    setSelectedTracks((prev) =>
      prev.map((t) => (t.name === name ? { ...t, stem } : t))
    );
  };

  const hasSelections = selectedTracks.length > 0;

  const keys = ["C major", "A minor", "G major", "E minor", "D major", "B minor", "A major", "F# minor", "E major", "C# minor", "B major", "G# minor", "F# major", "D# minor", "C# major", "A# minor",
    "F major", "D minor", "B♭ major", "G minor", "E♭ major", "C minor", "A♭ major", "F minor", "D♭ major", "B♭ minor", "G♭ major", "E♭ minor", "C♭ major", "A♭ minor"];
  
  const bpmDesc = "Beats Per Minute. Speed of musical composition."
  const durationDesc = "Length of output audio in seconds."
  const infStepsDesc = "Number of denoising steps. More steps means higher-quality output."
  const seedDesc = "Number used to control randomness. Use the same seed multiple times to generate the same output."
  const coverStrDesc = "How similar output audio is to input audio. We recommend using the value 0.7 for best results."
  const guidanceScaleDesc = "How similar output audio is to input prompt. We recommend using the value 0.3 for best results"
  const keyDesc = "Musical key signature."
  const thinkingDesc = "Enables ACE-Step's LLM to analyze input and structure coherent output. We recommend leaving this on for best results!"
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
                      <option value="drums">Drums</option>
                      <option value="bass">Bass</option>
                      <option value="guitar">Guitar</option>
                      <option value="piano">Piano</option>
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

          {/* Hyperparameters */}
          <div style={{ flexShrink: 0 }}>
            <div className="section-label">Parameters</div>
            <div className="parameters-grid">
              <NumberInput label="BPM"              desc={bpmDesc} value={bpm}            onChange={setBpm}            min={60}  max={120} />
              <NumberInput label="Duration (s)"     desc={durationDesc} value={duration}       onChange={setDuration}       min={30}   max={120}  />
              <NumberInput label="Inference Steps"  desc={infStepsDesc} value={inferenceSteps} onChange={setInferenceSteps} min={15}   max={30} />
              <NumberInput label="Seed"             desc={seedDesc} value={seed}           onChange={setSeed}           min={-1}            />
              <NumberInput label="Cover Strength"   desc={coverStrDesc} value={coverStrength}  onChange={setCoverStrength}  min={0}   max={1.0}  step={0.1}/>
              <NumberInput label="Guidance Scale"   desc={guidanceScaleDesc} value={guidanceScale}  onChange={setGuidanceScale}  min={0}   max={1.0}  step={0.1}/>
              <DropdownInput label="Key"            desc={keyDesc} valueArray={keys}      onChange={setKey}                                />
              <BooleanInput label="Thinking"        desc={thinkingDesc} value={isThinking}     onChange={setThinking}/>
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
          <div className="bottom-right" style={{ overflowY: "auto", display: "flex", flexDirection: "column", gap: 28 }}>

            {/* Generated Output */}
            <div>
              <div className="section-label">Generated Output</div>

              {isLoading && (
                <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-small)" }}>
                  Generating output, this may take a minute...
                </p>
              )}

              {stemResult && !isLoading && (
                <AudioPlayer src={stemResult.audioUrl} filename={stemResult.filename} />
              )}
            </div>

            {/* Attribution */}
            {stemResult && !isLoading && (
              <div>
                <div className="section-label">Attribution</div>
                <AttributionTable tracks={stemResult.tracks} />
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

export default App;