import React, { useState, useEffect } from 'react';
import CourseRecommendations from '../recommendations/CourseRecommendations';

const RightPanel = () => {
  const [chat_data, set_chat_data] = useState(null);

  useEffect(() => {
    const handle_chat_complete = (event) => {
      set_chat_data(event.detail);
    };

    // Add event listener
    document.addEventListener('chat-complete', handle_chat_complete);

    // Cleanup
    return () => {
      document.removeEventListener('chat-complete', handle_chat_complete);
    };
  }, []);

  return (
    <div className="right-panel">
      <CourseRecommendations chatData={chat_data} />
    </div>
  );
};

export default RightPanel; 