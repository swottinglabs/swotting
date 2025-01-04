import React, { useState } from 'react';
import { BiSend } from 'react-icons/bi';

const ChatInput = ({ onSubmit }) => {
  const [input, set_input] = useState('');

  const handle_submit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input);
      set_input('');
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handle_submit}>
      <input
        type="text"
        value={input}
        onChange={(e) => set_input(e.target.value)}
        placeholder="Type your message..."
        className="chat-input"
      />
      <button type="submit" className="chat-submit-button">
        <BiSend />
      </button>
    </form>
  );
};

export default ChatInput; 