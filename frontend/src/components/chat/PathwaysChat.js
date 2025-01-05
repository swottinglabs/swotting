import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import MultipleChoiceWithText from './MultipleChoiceWithText';
import RangeSlider from './RangeSlider';

const PathwaysChat = ({ onComplete }) => {
  const [messages, set_messages] = useState([]);
  const [current_step, set_current_step] = useState(0);
  const [user_data, set_user_data] = useState({});
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
      question: "What's your age?",
      type: "text"
    },
    {
      question: "What's your current occupation?",
      type: "multiple_choice_text",
      options: ["School", "College", "Work", "Nothing"],
      allowCustom: true
    },
    {
      question: "What's your goal?",
      type: "multiple_choice_text",
      options: ["Switch job", "Learn something new", "Not sure what to study"],
      allowCustom: true
    },
    {
      question: "What are your hobbies? (e.g., sports, movies, YouTube interests)",
      type: "text"
    },
    {
      question: "How would you describe your personality?",
      type: "multiple_choice",
      options: ["Extraverted", "Introverted", "Somewhere in between"]
    },
    {
      question: "What do you enjoy doing in group projects?",
      type: "text"
    },
    {
      question: "What do others say you're really good at?",
      type: "text"
    },
    {
      question: "Which subjects/topics did you enjoy in school or personal time?",
      type: "text"
    },
    {
      question: "How many hours per week can you dedicate to learning?",
      type: "multiple_choice",
      options: ["0-2 hours", "2-5 hours", "5-10 hours", "10+ hours"]
    }
  ];

  // Initial question
  useEffect(() => {
    set_messages([
      { text: chat_flow[0].question, sender: 'bot' }
    ]);
  }, []);

  const handle_response = async (response) => {
    // Add user response to messages
    set_messages(prev => [...prev, { text: String(response), sender: 'user' }]);
    
    // Store response in user data
    set_user_data(prev => ({
      ...prev,
      [current_step]: response
    }));

    // Move to next step
    const next_step = current_step + 1;
    
    if (next_step < chat_flow.length) {
      // Add next question
      set_messages(prev => [...prev, { text: chat_flow[next_step].question, sender: 'bot' }]);
      set_current_step(next_step);
    } else {
      // Chat complete, make API call
      try {
        const response = await fetch('https://api.example.com/pathways', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(user_data)
        });
        
        onComplete({
          ...user_data,
          type: 'pathways'
        });
      } catch (error) {
        console.error('Pathways API call failed:', error);
      }
    }
  };

  const render_input = () => {
    const current_question = chat_flow[current_step];

    switch (current_question.type) {
      case 'slider':
        return (
          <RangeSlider
            min={current_question.config.min}
            max={current_question.config.max}
            value={user_data[current_step] || current_question.config.defaultValue}
            onChange={handle_response}
            label="Age"
          />
        );
      case 'multiple_choice_text':
        return (
          <MultipleChoiceWithText
            options={current_question.options}
            onSelect={handle_response}
            allowCustom={true}
          />
        );
      case 'multiple_choice':
        return (
          <MultipleChoiceWithText
            options={current_question.options}
            onSelect={handle_response}
            allowCustom={false}
          />
        );
      case 'text':
        return <ChatInput onSubmit={handle_response} />;
      default:
        return null;
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
          {render_input()}
        </div>
      )}
    </div>
  );
};

export default PathwaysChat; 