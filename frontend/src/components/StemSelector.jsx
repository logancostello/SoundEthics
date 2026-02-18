function StemSelector({ label, active = false, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "8px 18px",
        background: active ? "#e8d5b0" : "transparent",
        color: active ? "#0a0a0f" : "#666",
        border: "1px solid",
        borderColor: active ? "#e8d5b0" : "#2a2a3a",
        cursor: "pointer",
        fontSize: "12px",
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        fontFamily: "'Courier New', monospace",
        transition: "all 0.15s ease",
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.target.style.borderColor = "#3a3a5a";
          e.target.style.color = "#aaa";
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.target.style.borderColor = "#2a2a3a";
          e.target.style.color = "#666";
        }
      }}
    >
      {label}
    </button>
  );
}

export default StemSelector;
