import React from "react";

type Option = {
  value: string;
  label: string;
};

type RadioButtonsProps = {
  options: Option[];
  selected: string;
  onChange: (value: string) => void;
  name: string;
};

const RadioButtons: React.FC<RadioButtonsProps> = ({
  options,
  selected,
  onChange,
  name,
}) => {
  return (
    <div>
      {options.map((option) => (
        <div className="form-check" key={option.value}>
          <input
            className="form-check-input"
            type="radio"
            name={name}
            value={option.value}
            id={option.value}
            checked={selected === option.value}
            onChange={(e) => onChange(e.target.value)}
          />
          <label className="form-check-label" htmlFor={option.value}>
            {option.label}
          </label>
        </div>
      ))}
    </div>
  );
};

export default RadioButtons;
