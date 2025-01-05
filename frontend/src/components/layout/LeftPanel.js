import React, { useState } from 'react';
import NavigationButton from '../buttons/NavigationButton';
import { BiReset } from 'react-icons/bi';
import ChatBot from '../chat/ChatBot';
import QuickSearch from '../search/QuickSearch';
import PathwaysChat from '../chat/PathwaysChat';

const LeftPanel = () => {
  const [active_mode, set_active_mode] = useState(null);
  const [selected_mode, set_selected_mode] = useState(null);

  const buttons = [
    {   
        id: 'quick-search',
        text: 'Quick Search',
        tooltip: 'Directly performs a course search for the user\'s desired topic and displays the top 5 courses instantly.'
      },
  
      {
        id: 'build-curriculum',
        text: 'Build a curriculum',
        tooltip: 'Assists users with a clear topic in mind by building a step-by-step curriculum from their current knowledge to their goal, then recommends courses for each skill in the curriculum.'
      },
      {
        id: 'no-idea',
        text: 'No idea what to learn',
        tooltip: 'Guides users uncertain about their interests by exploring potential areas, learning their goals and skills through detailed questioning, and suggesting courses in intriguing fields.'
      }
  ];

  const handleReset = () => {
    set_active_mode(null);
    set_selected_mode(null);
    document.dispatchEvent(new Event('reset-panel'));
  };

  const handle_button_click = (button_id) => {
    set_selected_mode(button_id);
    set_active_mode(button_id);
  };

  const handle_completion = (data) => {
    // Dispatch event with the data for the right panel
    document.dispatchEvent(new CustomEvent('chat-complete', { 
      detail: { ...data, mode: selected_mode } 
    }));
  };

  const render_active_component = () => {
    switch(active_mode) {
      case 'quick-search':
        return <QuickSearch onComplete={handle_completion} />;
      case 'build-curriculum':
        return <ChatBot onComplete={handle_completion} />;
      case 'no-idea':
        return <PathwaysChat onComplete={handle_completion} />;
      default:
        return (
          <div className="button-container">
            {buttons.map((button, index) => (
              <div key={index} className="button-wrapper" data-tooltip={button.tooltip}>
                <NavigationButton 
                  text={button.text}
                  onClick={() => handle_button_click(button.id)}
                />
              </div>
            ))}
          </div>
        );
    }
  };

  return (
    <div className="left-panel">
      <div className="reset-icon-container">
        <BiReset 
          className="reset-icon" 
          onClick={handleReset}
          aria-label="Reset"
        />
      </div>
      <div className={`content-container ${active_mode ? 'mode-active' : ''}`}>
        {render_active_component()}
      </div>
    </div>
  );
};

export default LeftPanel; 