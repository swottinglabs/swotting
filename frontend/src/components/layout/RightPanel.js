import React, { useState, useEffect } from 'react';
import CourseCard from '../courses/CourseCard';
import LearningPlan from '../learning/LearningPlan';
import LoadingSpinner from '../common/LoadingSpinner';
import './RightPanel.css';

const RightPanel = () => {
  const [content, set_content] = useState(null);
  const [is_loading, set_is_loading] = useState(false);

  useEffect(() => {
    const handle_content_update = (event) => {
      set_content(event.detail);
      set_is_loading(false);
    };

    const handle_reset = () => {
      set_content(null);
      set_is_loading(false);
    };

    const handle_start_loading = () => {
      set_is_loading(true);
      set_content(null);
    };

    const handle_stop_loading = () => {
      set_is_loading(false);
    };

    // Add event listeners
    document.addEventListener('chat-complete', handle_content_update);
    document.addEventListener('search-complete', handle_content_update);
    document.addEventListener('reset-panel', handle_reset);
    document.addEventListener('start-loading', handle_start_loading);
    document.addEventListener('stop-loading', handle_stop_loading);

    // Cleanup
    return () => {
      document.removeEventListener('chat-complete', handle_content_update);
      document.removeEventListener('search-complete', handle_content_update);
      document.removeEventListener('reset-panel', handle_reset);
      document.removeEventListener('start-loading', handle_start_loading);
      document.removeEventListener('stop-loading', handle_stop_loading);
    };
  }, []);

  const render_content = () => {
    if (is_loading) {
      return <LoadingSpinner />;
    }

    if (!content) {
      return (
        <div className="empty-state">
          <p>Select an option from the left panel to start exploring courses.</p>
        </div>
      );
    }

    if (content.type === 'curriculum') {
      return <LearningPlan learning_plan={content.curriculum.learning_plan} />;
    }

    // Default search results view
    return (
      <div className="search-results">
        <h2 className="results-header">
          Courses for "{content.query}"
        </h2>
        <div className="courses-grid">
          {content.results.map((course) => (
            <CourseCard key={course.uuid} course={course} />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="right-panel">
      {render_content()}
    </div>
  );
};

export default RightPanel; 