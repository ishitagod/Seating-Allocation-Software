import React from "react";

export interface DropdownOption {
  value: string;
  label: string;
}

interface DropdownProps {
  options: DropdownOption[];
  selected: string;
  onSelect: (value: string) => void;
  buttonClassName?: string; // e.g., "btn btn-primary"
  id?: string;
}

function Dropdown({
  options,
  selected,
  onSelect,
  buttonClassName = "btn btn-secondary",
  id = "dropdownMenu",
}: DropdownProps) {
  return (
    <div className="dropdown">
      <button
        className={`${buttonClassName} dropdown-toggle`}
        type="button"
        id={id}
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {options.find((option) => option.value === selected)?.label || "Select"}
      </button>
      <ul className="dropdown-menu" aria-labelledby={id}>
        {options.map((option) => (
          <li key={option.value}>
            <button
              type="button" // Explicitly setting type to "button"
              className="dropdown-item"
              onClick={() => onSelect(option.value)}
            >
              {option.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dropdown;
