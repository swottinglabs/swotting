import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const TextQuestion = ({ question, onSubmit }) => {
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (answer.trim()) {
      onSubmit(answer.trim());
      setAnswer('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="font-semibold">{question}</p>
      <div className="flex space-x-2">
        <Input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer..."
          className="flex-grow"
        />
        <Button type="submit">Submit</Button>
      </div>
    </form>
  );
};

TextQuestion.propTypes = {
  question: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

TextQuestion.defaultProps = {
  question: '',
};

export default TextQuestion; 