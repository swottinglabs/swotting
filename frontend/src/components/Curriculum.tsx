import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type CurriculumProps = {
  curriculum: Array<{ skill: string; courses: Array<{ title: string; link: string }> }> | null
}

const Curriculum: React.FC<CurriculumProps> = ({ curriculum }) => {
  if (!curriculum) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Course Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Your recommended courses will appear here once you've completed the chatbot interaction.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {curriculum.length === 1 && curriculum[0].skill
            ? `Courses related to "${curriculum[0].skill}"`
            : 'Your Personalized Curriculum'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {curriculum.map((item, index) => (
          <div key={index} className="mb-4">
            {curriculum.length > 1 && <h3 className="font-semibold text-lg mb-2">{item.skill}</h3>}
            <ul className="list-disc pl-5">
              {item.courses.map((course, courseIndex) => (
                <li key={courseIndex} className="mb-2">
                  <a href={course.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {course.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default Curriculum

