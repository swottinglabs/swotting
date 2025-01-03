import React from 'react'
import { Button } from '@/components/ui/button'

type Option = {
  label: string
  value: string
}

type MultipleChoiceQuestionProps = {
  question: string
  options: Option[]
  onSelect: (value: string) => void
}

const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({ question, options, onSelect }) => {
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
  )
}

export default MultipleChoiceQuestion

