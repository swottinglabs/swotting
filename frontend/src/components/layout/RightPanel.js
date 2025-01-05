import React, { useState, useEffect } from 'react';
import CourseCard from '../courses/CourseCard';
import './RightPanel.css';

const RightPanel = () => {
  const [search_results, set_search_results] = useState(null);

  useEffect(() => {
    const handle_search_complete = (event) => {
      set_search_results(event.detail);
    };

    const handle_reset = () => {
      set_search_results(null);
    };

    // Add event listeners
    document.addEventListener('search-complete', handle_search_complete);
    document.addEventListener('reset-panel', handle_reset);

    // Cleanup
    return () => {
      document.removeEventListener('search-complete', handle_search_complete);
      document.removeEventListener('reset-panel', handle_reset);
    };
  }, []);

  return (
    <div className="right-panel">
      {search_results ? (
        <div className="search-results">
          <h2 className="results-header">
            Courses for "{search_results.query}"
          </h2>
          <div className="courses-grid">
            {search_results.results.map((course) => (
              <CourseCard key={course.uuid} course={course} />
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <h2>Welcome to Swotting</h2>
          <p>Select an option from the left panel to start exploring courses.</p>
        </div>
      )}
    </div>
  );
};

export default RightPanel; 