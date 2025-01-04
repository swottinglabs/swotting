import React from 'react';

const NavigationButton = ({ text, onClick }) => {
  return (
    <button 
      className="navigation-button"
      onClick={onClick}
    >
      {text}
    </button>
  );
};

export default NavigationButton; 