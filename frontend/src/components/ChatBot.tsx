'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import MultipleChoiceQuestion from './MultipleChoiceQuestion'
import TextQuestion from './TextQuestion'
import { searchCourses } from '@/utils/searchCourses'
import { RotateCcw } from 'lucide-react'

type Message = {
  type: 'user' | 'bot'
  content: string | React.ReactNode
}

type ChatBotProps = {
  setCurriculum: React.Dispatch<React.SetStateAction<Array<{ skill: string; courses: Array<{ title: string; link: string }> }> | null>>
  resetCurriculum: () => void
}

const ChatBot: React.FC<ChatBotProps> = ({ setCurriculum, resetCurriculum }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [userProfile, setUserProfile] = useState<Record<string, any>>({})
  const [showInitialOptions, setShowInitialOptions] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleUserInput = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isWaitingForResponse) {
      addMessage('user', input)
      processUserInput(input)
      setInput('')
      setIsWaitingForResponse(true)
    }
  }

  const addMessage = (type: 'user' | 'bot', content: string | React.ReactNode) => {
    setMessages(prev => [...prev, { type, content }])
    setShowInitialOptions(false)
  }

  const processUserInput = (userInput: string) => {
    const command = userInput.toLowerCase().trim()
    switch (currentStep) {
      case 'pathways_choose_area':
        handleChosenArea(userInput)
        break
      case 'quick_search':
        handleSearch()
        break;
      case null:
        switch (command) {
          case 'help':
            handleHelp()
            break
          case 'q':
            handleQuickSearch()
            break
          case 'explorer':
            handleExplorer()
            break
          case 'pathways':
            handlePathways()
            break
          default:
            handleExplorer()
        }
        break
      default:
        handleBotResponse("I'm sorry, I didn't understand that. Please try again or type 'help' for assistance.")
    }
  }

  const handleBotResponse = (response: string | React.ReactNode) => {
    setTimeout(() => {
      addMessage('bot', response)
      setIsWaitingForResponse(false)
    }, 500)
  }

  const handleHelp = () => {
    const helpMessage = (
      <div>
        <p>This chatbot helps you find the right courses for your needs. Available options:</p>
        <ul className="list-disc pl-5 mt-2">
          <li>Help: Display this help message</li>
          <li>Quick Search: Search for courses</li>
          <li>Explorer: Build a curriculum based on your goals</li>
          <li>Pathways: Explore different learning paths</li>
        </ul>
      </div>
    )
    handleBotResponse(helpMessage)
  }

  const handleQuickSearch = () => {
    setShowInitialOptions(false)
    setCurrentStep('quick_search')
    setSearchQuery('')
    handleBotResponse(
      <div className="flex flex-col items-center justify-center h-full">
        <h2 className="text-2xl font-bold mb-4">Quick Course Search</h2>
        <p className="text-center mb-4">Enter a topic to find relevant courses:</p>
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            type="text"
            placeholder="e.g., JavaScript, Machine Learning"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button type="button" onClick={handleSearch}>Search</Button>
        </div>
      </div>
    )
  }

  const handleSearch = async () => {
    if (searchQuery.trim()) {
      handleBotResponse(`Searching for courses related to "${searchQuery}"...`)
      try {
        const courses = await searchCourses(searchQuery)
        setCurriculum([{ skill: searchQuery, courses: courses.map(course => ({ title: course.title, link: course.link })) }])
        handleBotResponse(`I've found some courses related to "${searchQuery}". You can see them on the right side of the screen.`)
      } catch (error) {
        handleBotResponse("Sorry, I couldn't fetch the courses at the moment. Please try again later.")
      }
    }
  }


  const handleExplorer = () => {
    setCurrentStep('explorer_goal')
    handleBotResponse(
      <TextQuestion
        question="What specific topic or skill would you like to learn more about?"
        onSubmit={(answer) => {
          setUserProfile({ ...userProfile, goal: answer })
          setCurrentStep('explorer_current_knowledge')
          handleBotResponse(
            <TextQuestion
              question={`Great! You want to learn more about ${answer}. What's your current level of knowledge in this area?`}
              onSubmit={handleExplorerCurrentKnowledge}
            />
          )
        }}
      />
    )
  }

  const handleExplorerCurrentKnowledge = (answer: string) => {
    setUserProfile({ ...userProfile, currentKnowledge: answer })
    // Here you would normally call an API to generate a curriculum based on the user's goal and current knowledge
    // For this example, we'll use a mock curriculum
    const mockCurriculum = [
      { skill: 'Fundamentals', courses: ['Course A', 'Course B'] },
      { skill: 'Intermediate Concepts', courses: ['Course C'] },
      { skill: 'Advanced Techniques', courses: ['Course D', 'Course E'] },
    ]
    displayCurriculum(mockCurriculum)
  }

  const displayCurriculum = async (curriculum: Array<{ skill: string; courses: string[] }>) => {
    const curriculumWithCourses = await Promise.all(curriculum.map(async (item) => {
      const courses = await searchCourses(item.skill)
      return {
        skill: item.skill,
        courses: courses.slice(0, 2).map(course => ({ title: course.title, link: course.link }))
      }
    }))

    setCurriculum(curriculumWithCourses)
    handleBotResponse("I've prepared a personalized curriculum for you. You can see it on the right side of the screen.")
    setCurrentStep(null)
  }

  const handlePathways = () => {
    setCurrentStep('pathways_age')
    handleBotResponse(
      <TextQuestion
        question="To help you explore different learning paths, let's start by getting to know you better. What's your age?"
        onSubmit={(answer) => {
          setUserProfile({ ...userProfile, age: answer })
          setCurrentStep('pathways_occupation')
          handleBotResponse(
            <MultipleChoiceQuestion
              question="What's your current occupation?"
              options={[
                { label: 'Student (School)', value: 'school' },
                { label: 'Student (College)', value: 'college' },
                { label: 'Employed', value: 'employed' },
                { label: 'Unemployed', value: 'unemployed' },
                { label: 'Other', value: 'other' },
              ]}
              onSelect={handlePathwaysOccupation}
            />
          )
        }}
      />
    )
  }

  const handlePathwaysOccupation = (answer: string) => {
    setUserProfile({ ...userProfile, occupation: answer })
    setCurrentStep('pathways_goal')
    handleBotResponse(
      <MultipleChoiceQuestion
        question="What's your primary goal for learning?"
        options={[
          { label: 'Switch careers', value: 'switch_career' },
          { label: 'Learn something new', value: 'learn_new' },
          { label: 'Advance in current career', value: 'advance_career' },
          { label: 'Not sure, just exploring', value: 'exploring' },
        ]}
        onSelect={handlePathwaysGoal}
      />
    )
  }

  const handlePathwaysGoal = (answer: string) => {
    setUserProfile({ ...userProfile, goal: answer })
    // Here you would normally call an API to suggest areas based on the user's profile
    // For this example, we'll use mock suggested areas
    const mockSuggestedAreas = [
      'Web Development',
      'Data Science',
      'Digital Marketing',
      'UX/UI Design',
      'Artificial Intelligence',
    ]
    displaySuggestedAreas(mockSuggestedAreas)
  }

  const displaySuggestedAreas = (areas: string[]) => {
    const areasDisplay = (
      <div>
        <h3 className="font-bold mb-2">Suggested Areas to Explore:</h3>
        <ul className="list-disc pl-5">
          {areas.map((area, index) => (
            <li key={index}>{area}</li>
          ))}
        </ul>
        <p className="mt-4">Which area would you like to explore further?</p>
      </div>
    )
    handleBotResponse(areasDisplay)
    setCurrentStep('pathways_choose_area')
  }

  const handleChosenArea = (area: string) => {
    setUserProfile({ ...userProfile, chosenArea: area })
    handleBotResponse(`Great choice! Let's explore ${area} in more detail.`)
    // Here you would normally call an API to get specific skills and courses for the chosen area
    // For this example, we'll use mock data
    const mockSkillsAndCourses = [
      { skill: 'Fundamentals of ' + area, courses: ['Course X', 'Course Y'] },
      { skill: 'Intermediate ' + area, courses: ['Course Z'] },
      { skill: 'Advanced ' + area, courses: ['Course W'] },
    ]
    displayCurriculum(mockSkillsAndCourses)
  }

  const handleOptionClick = (option: string) => {
    switch (option) {
      case 'pathways':
        handlePathways()
        break
      case 'explorer':
        handleExplorer()
        break
      case 'quick_search':
        handleQuickSearch()
        break
      case 'help':
        handleHelp()
        break
    }
  }

  const handleReset = () => {
    setMessages([])
    setInput('')
    setIsWaitingForResponse(false)
    setCurrentStep(null)
    setUserProfile({})
    setShowInitialOptions(true)
    setSearchQuery('')
    resetCurriculum()
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-end mb-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleReset}
          aria-label="Reset chat"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>
      <ScrollArea className="flex-grow mb-4">
        {showInitialOptions ? (
          <div className="flex flex-col items-center justify-center h-full space-y-4">
            <h2 className="text-2xl font-bold mb-4">Welcome to the Course Recommendation Chatbot</h2>
            <p className="text-center mb-4">Choose an option to get started:</p>
            <div className="grid grid-cols-2 gap-4">
              <Button onClick={() => handleOptionClick('pathways')} className="w-full">Pathways</Button>
              <Button onClick={() => handleOptionClick('explorer')} className="w-full">Explorer</Button>
              <Button onClick={() => handleOptionClick('quick_search')} className="w-full">Quick Search</Button>
              <Button onClick={() => handleOptionClick('help')} className="w-full">Help</Button>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <Card key={index} className={`mb-4 ${message.type === 'user' ? 'bg-blue-100' : 'bg-green-100'}`}>
              <CardContent className="p-4">
                {typeof message.content === 'string' ? (
                  <p>{message.content}</p>
                ) : (
                  message.content
                )}
              </CardContent>
            </Card>
          ))
        )}
        <div ref={messagesEndRef} />
      </ScrollArea>
      {!showInitialOptions && currentStep !== 'quick_search' && (
        <form onSubmit={handleUserInput} className="flex">
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-grow"
            disabled={isWaitingForResponse}
          />
          <Button type="submit" className="ml-2" disabled={isWaitingForResponse}>
            Send
          </Button>
        </form>
      )}
    </div>
  )
}

export default ChatBot

