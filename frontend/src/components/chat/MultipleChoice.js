import React from 'react';

const MultipleChoice = ({ options, onSelect }) => {
  return (
    <div className="multiple-choice-container">
      {options.map((option, index) => (
        <button
          key={index}
          className="multiple-choice-button"
          onClick={() => onSelect(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
};

export default MultipleChoice; 