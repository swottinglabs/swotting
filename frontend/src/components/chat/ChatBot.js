import React, { useState, useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import MultipleChoice from './MultipleChoice';
import { api } from '../../services/api';

const ChatBot = ({ onComplete }) => {
  const [messages, set_messages] = useState([]);
  const [current_step, set_current_step] = useState(0);
  const [user_data, set_user_data] = useState({});
  const [is_chat_complete, set_is_chat_complete] = useState(false);
  const messages_end_ref = useRef(null);

  const scroll_to_bottom = () => {
    messages_end_ref.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll to bottom when messages update
  useEffect(() => {
    scroll_to_bottom();
  }, [messages]);

  const chat_flow = [
    {
      question: "What do you want to learn?",
      type: "text"
    },
    {
      question: "What is your current knowledge in this area?",
      type: "text"
    }
  ];

  // Show initial question when component mounts
  useEffect(() => {
    set_messages([
      { text: chat_flow[0].question, sender: 'bot' }
    ]);
  }, []);

  // Handle API call when chat is complete
  useEffect(() => {
    const generate_curriculum = async () => {
      if (!is_chat_complete) return;

      try {
        // Dispatch loading event before making API call
        document.dispatchEvent(new CustomEvent('start-loading'));
        
        const response = await api.generateCurriculum({
          desired_skill: user_data[0],
          current_knowledge: user_data[1]
        });
        
        console.log('Curriculum generation response:', response);
        
        onComplete({
          desired_skill: user_data[0],
          current_knowledge: user_data[1],
          curriculum: response,
          type: 'curriculum'
        });
      } catch (error) {
        console.error('Curriculum generation failed:', error);
        set_messages(prev => [...prev, { 
          text: "Sorry, there was an error generating your curriculum. Please try again.", 
          sender: 'bot' 
        }]);
        // Reset chat completion state to allow retry
        set_is_chat_complete(false);
        // Stop loading on error
        document.dispatchEvent(new CustomEvent('stop-loading'));
      }
    };

    generate_curriculum();
  }, [is_chat_complete, user_data, onComplete]);

  const handle_message = async (message) => {
    // Add user message to chat
    set_messages(prev => [...prev, { text: message, sender: 'user' }]);
    
    // Store response in user data
    set_user_data(prev => ({
      ...prev,
      [current_step]: message
    }));
    
    // Move to next step
    const next_step = current_step + 1;
    
    if (next_step < chat_flow.length) {
      // Add next bot question to chat
      set_messages(prev => [...prev, { text: chat_flow[next_step].question, sender: 'bot' }]);
      set_current_step(next_step);
    } else {
      // Mark chat as complete after all updates
      set_current_step(next_step);
      set_is_chat_complete(true);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage 
            key={index}
            text={message.text}
            sender={message.sender}
          />
        ))}
        <div ref={messages_end_ref} className="messages-end" />
      </div>
      
      {current_step < chat_flow.length && (
        <div className="input-container">
          {chat_flow[current_step].type === 'text' ? (
            <ChatInput onSubmit={handle_message} />
          ) : (
            <MultipleChoice 
              options={chat_flow[current_step].options}
              onSelect={handle_message}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default ChatBot; 