import React, { useState } from 'react';

const MultipleChoiceWithText = ({ options, onSelect, allowCustom = false, customLabel = "Other" }) => {
  const [selected_option, set_selected_option] = useState('');
  const [custom_text, set_custom_text] = useState('');

  const handle_submit = (option) => {
    if (option === 'other' && allowCustom) {
      set_selected_option('other');
    } else {
      set_selected_option(option);
      onSelect(option);
    }
  };

  const handle_custom_submit = (e) => {
    e.preventDefault();
    if (custom_text.trim()) {
      onSelect(custom_text);
    }
  };

  return (
    <div className="multiple-choice-container">
      {options.map((option, index) => (
        <button
          key={index}
          className={`multiple-choice-button ${selected_option === option ? 'selected' : ''}`}
          onClick={() => handle_submit(option)}
        >
          {option}
        </button>
      ))}
      
      {allowCustom && (
        <button
          className={`multiple-choice-button ${selected_option === 'other' ? 'selected' : ''}`}
          onClick={() => handle_submit('other')}
        >
          {customLabel}
        </button>
      )}

      {selected_option === 'other' && allowCustom && (
        <form onSubmit={handle_custom_submit} className="custom-input-form">
          <input
            type="text"
            value={custom_text}
            onChange={(e) => set_custom_text(e.target.value)}
            placeholder="Please specify..."
            className="custom-input"
          />
          <button type="submit" className="custom-submit-button">
            Submit
          </button>
        </form>
      )}
    </div>
  );
};

export default MultipleChoiceWithText; 