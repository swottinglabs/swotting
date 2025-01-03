import React from 'react';

function ChatBot({ setCurriculum, resetCurriculum }) {
  return (
    <div className="chat_bot_container">
      <h2>AI Learning Path Generator</h2>
      {/* Chat interface will go here */}
      <button onClick={resetCurriculum}>Reset Curriculum</button>
    </div>
  );
}

export default ChatBot; 