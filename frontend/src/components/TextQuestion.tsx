import React, { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

type TextQuestionProps = {
  question: string
  onSubmit: (answer: string) => void
}

const TextQuestion: React.FC<TextQuestionProps> = ({ question, onSubmit }) => {
  const [answer, setAnswer] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (answer.trim()) {
      onSubmit(answer.trim())
      setAnswer('')
    }
  }

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
  )
}

export default TextQuestion

