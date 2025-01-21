import React, { useState, useEffect } from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
    const loading_messages = [
        "Building Curriculum...",
        "Assessing Skills...",
        "Searching Courses...",
        "Analyzing Learning Paths...",
        "Finding Best Resources...",
        "Organizing Content...",
        "Tailoring to Your Level...",
        "Curating Quality Content..."
    ];

    const [current_message, set_current_message] = useState(
        loading_messages[Math.floor(Math.random() * loading_messages.length)]
    );

    useEffect(() => {
        const interval = setInterval(() => {
            set_current_message(loading_messages[Math.floor(Math.random() * loading_messages.length)]);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="loading-container">
            <div className="spinner"></div>
            <div className="loading-text">{current_message}</div>
        </div>
    );
};

export default LoadingSpinner; 