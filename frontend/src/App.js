import React, { useState } from 'react';
import './App.css';
import ChatBot from './components/ChatBot';
import Curriculum from './components/Curriculum';

function App() {
  const [curriculum, setCurriculum] = useState(null);

  return (
    <div className="app">
      <header className="app_header">
        <h1>Learning Resources Aggregator</h1>
      </header>
      <main className="app_main">
        <div className="flex_container">
          <div className="chat_section">
            <ChatBot 
              setCurriculum={setCurriculum} 
              resetCurriculum={() => setCurriculum(null)} 
            />
          </div>
          <div className="curriculum_section">
            <Curriculum curriculum={curriculum} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 