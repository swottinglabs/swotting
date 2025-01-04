import React from 'react';

const ChatMessage = ({ text, sender }) => {
  return (
    <div className={`chat-message ${sender}-message`}>
      {text}
    </div>
  );
};

export default ChatMessage; 