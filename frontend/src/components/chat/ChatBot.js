import React, { useState, useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import MultipleChoice from './MultipleChoice';

const ChatBot = ({ onComplete }) => {
  const [messages, set_messages] = useState([]);
  const [current_step, set_current_step] = useState(0);
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
    },
    {
      question: "How many hours do you want to spend learning per week?",
      type: "multiple_choice",
      options: [
        "0-2 hours",
        "2-5 hours",
        "5-10 hours",
        "10+ hours"
      ]
    }
  ];

  // Show initial question when component mounts
  useEffect(() => {
    set_messages([
      { text: chat_flow[0].question, sender: 'bot' }
    ]);
  }, []);

  const handle_message = async (message) => {
    // Add user message to chat
    set_messages(prev => [...prev, { text: message, sender: 'user' }]);
    
    // Move to next step
    const next_step = current_step + 1;
    
    if (next_step < chat_flow.length) {
      // Add next bot question to chat
      set_messages(prev => [...prev, { text: chat_flow[next_step].question, sender: 'bot' }]);
    }
    
    if (current_step === chat_flow.length - 1) {
      // Make demo API call
      try {
        const response = await fetch('https://api.example.com/recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            topic: messages[1].text,
            current_knowledge: messages[3].text,
            hours_per_week: message
          })
        });
        
        // For demo purposes, we'll just move forward
        onComplete({
          topic: messages[1].text,
          current_knowledge: messages[3].text,
          hours_per_week: message
        });
      } catch (error) {
        console.error('API call failed:', error);
      }
    }
    
    set_current_step(next_step);
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