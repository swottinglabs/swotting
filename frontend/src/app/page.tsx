'use client'

import { useState } from 'react'
import ChatBot from '@/components/ChatBot'
import Curriculum from '@/components/Curriculum'

export default function Home() {
  const [curriculum, setCurriculum] = useState<Array<{ skill: string; courses: Array<{ title: string; link: string }> }> | null>(null)

  return (
    <div className="flex h-screen">
      <div className="w-1/2 bg-gray-100 p-4 overflow-y-auto">
        <ChatBot 
          setCurriculum={setCurriculum} 
          resetCurriculum={() => setCurriculum(null)} 
        />
      </div>
      <div className="w-1/2 bg-white p-4 overflow-y-auto">
        <Curriculum curriculum={curriculum} />
      </div>
    </div>
  )
}

