import React from 'react';
import './App.css';
import LeftPanel from './components/layout/LeftPanel';
import RightPanel from './components/layout/RightPanel';

function App() {
  return (
    <div className="app">
      <LeftPanel />
      <RightPanel />
    </div>
  );
}

export default App;
