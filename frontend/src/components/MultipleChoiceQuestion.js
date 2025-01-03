import React from 'react';
import PropTypes from 'prop-types';
import { Button } from '../components/ui/button';

const MultipleChoiceQuestion = ({ question, options, onSelect }) => {
  return (
    <div className="space-y-4">
      <p className="font-semibold">{question}</p>
      <div className="space-y-2">
        {options.map((option) => (
          <Button
            key={option.value}
            onClick={() => onSelect(option.value)}
            variant="outline"
            className="w-full justify-start text-left"
          >
            {option.label}
          </Button>
        ))}
      </div>
    </div>
  );
};

MultipleChoiceQuestion.propTypes = {
  question: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSelect: PropTypes.func.isRequired,
};

MultipleChoiceQuestion.defaultProps = {
  options: [],
};

export default MultipleChoiceQuestion; 