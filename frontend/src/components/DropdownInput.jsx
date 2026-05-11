import { useState, useEffect } from "react";

export default function DropdownInput({ label, valueArray }) {
    const [selected, setSelected] = useState("Key")
    const [open, setOpen] = useState(false)

    let handleChange = (e) => {
        setSelected(e.target.value)
    }

    return (
        <div className="dropdown-input">
            <span className="dropdown-label">{label}</span>
            <select className="dropdown-select" onChange={handleChange}>
                <option value="" disabled selected>Select a Key</option>
                {valueArray.map(element => <option key={element} value={element}>{element}</option>)}
            </select>
        </div>
    )
}