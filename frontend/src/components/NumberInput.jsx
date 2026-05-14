import { useState, useEffect } from "react";

export default function NumberInput({ label, desc, value, onChange, min, max, step = 1, placeholder }) {
  const [raw, setRaw] = useState(String(value));

  // keep raw in sync if parent changes value externally
  useEffect(() => {
    setRaw(String(value));
  }, [value]);

  const handleChange = (e) => {
    const input = e.target.value;

    // allow empty string or a lone minus sign while typing
    if (input === "" || input === "-") {
      setRaw(input);
      return;
    }

    const num = Number(input);
    if (isNaN(num)) return;

    if (max !== undefined && num > max) {
      setRaw(String(max));
      onChange(max);
    } else {
      setRaw(input);
      onChange(num);
    }
  };

  const handleBlur = () => {
    let num = Number(raw);
    if (raw === "" || raw === "-" || isNaN(num)) num = min ?? 0;
    if (min !== undefined && num < min) num = min;
    if (max !== undefined && num > max) num = max;
    setRaw(String(num));
    onChange(num);
  };

  return (
    <div className="number-input">
      <span className="number-input-label" title={desc}>{label}</span>
      <input
        type="number"
        value={raw}
        onChange={handleChange}
        onBlur={handleBlur}
        min={min}
        max={max}
        step={step}
        placeholder={placeholder}
        className="number-input-field"
      />
    </div>
  );
}