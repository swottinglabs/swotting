import React, { useState } from 'react';
import { BiSearch } from 'react-icons/bi';
import { api } from '../../services/api';

const QuickSearch = ({ onComplete }) => {
  const [search_term, set_search_term] = useState('');

  const handle_submit = async (e) => {
    e.preventDefault();
    if (!search_term.trim()) return;

    try {
      const response = await api.get(`/search/?q=${encodeURIComponent(search_term)}`);
      console.log('Search results:', response);
      
      // Dispatch event for RightPanel
      const event = new CustomEvent('search-complete', {
        detail: response
      });
      document.dispatchEvent(event);

      if (onComplete) {
        onComplete({
          search_term: search_term,
          type: 'quick_search',
          results: response.results
        });
      }
    } catch (error) {
      console.error('Quick search API call failed:', error);
    }
  };

  return (
    <div className="quick-search-container">
      <form onSubmit={handle_submit} className="quick-search-form">
        <div className="search-input-container">
          <BiSearch className="search-icon" />
          <input
            type="text"
            value={search_term}
            onChange={(e) => set_search_term(e.target.value)}
            placeholder="Enter a topic to search..."
            className="search-input"
          />
        </div>
        <button type="submit" className="search-button">
          Search
        </button>
      </form>
    </div>
  );
};

export default QuickSearch; 