export default function BooleanInput({ label, desc, value, onChange }) {
  return (
    <div className="number-input">
      <span className="number-input-label" title={desc}>{label}</span>
      <button
        role="switch"
        aria-checked={value}
        onClick={() => onChange(!value)}
        style={{
          width: 36,
          height: 20,
          borderRadius: 10,
          border: "none",
          padding: 0,
          cursor: "pointer",
          position: "relative",
          flexShrink: 0,
          background: value ? "var(--color-text-primary, #111)" : "var(--color-border-secondary, #ccc)",
          transition: "background 0.18s",
        }}
      >
        <span
          style={{
            display: "block",
            position: "absolute",
            top: 3,
            left: 3,
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: "white",
            transition: "transform 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
            transform: value ? "translateX(16px)" : "translateX(0)",
            pointerEvents: "none",
          }}
        />
      </button>
    </div>
  );
}