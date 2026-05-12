import { useState, useEffect } from "react";

export default function DropdownInput({ label, valueArray, onChange }) {
    const [selected, setSelected] = useState("Key")
    const [open, setOpen] = useState(false)

    let handleChange = (e) => {
        setSelected(e.target.value);
        onChange(e.target.value);
    }

    return (
        <div className="dropdown-input">
            <span className="dropdown-label">{label}</span>
            <select className="dropdown-select" onChange={handleChange}>
                <option className="dropdown-option" value="" selected>Select a Key</option>
                {valueArray.map(element => <option className="dropdown-option" key={element} value={element}>{element}</option>)}
            </select>
        </div>
    )
}