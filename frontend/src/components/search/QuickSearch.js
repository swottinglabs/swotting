import React, { useState } from 'react';
import { BiSearch } from 'react-icons/bi';

const QuickSearch = ({ onComplete }) => {
  const [search_term, set_search_term] = useState('');

  const handle_submit = async (e) => {
    e.preventDefault();
    if (!search_term.trim()) return;

    try {
      // Demo API call
      const response = await fetch('https://api.example.com/quick-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_term: search_term
        })
      });
      
      // For demo purposes, we'll just pass the search term
      onComplete({
        search_term: search_term,
        type: 'quick_search'
      });
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