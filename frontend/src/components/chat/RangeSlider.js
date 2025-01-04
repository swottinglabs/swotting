import React from 'react';

const RangeSlider = ({ min, max, value, onChange, label }) => {
  return (
    <div className="range-slider-container">
      <div className="range-slider-label">
        {label}: <span className="range-value">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="range-slider"
      />
      <div className="range-marks">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
};

export default RangeSlider; 