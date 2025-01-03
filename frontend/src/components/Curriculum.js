import React from 'react';

function Curriculum({ curriculum }) {
  if (!curriculum) {
    return (
      <div className="curriculum_placeholder">
        <h2>Your Learning Path</h2>
        <p>Generate a curriculum using the chat interface</p>
      </div>
    );
  }

  return (
    <div className="curriculum_container">
      <h2>Your Learning Path</h2>
      {curriculum.map((section, index) => (
        <div key={index} className="skill_section">
          <h3>{section.skill}</h3>
          <ul>
            {section.courses.map((course, courseIndex) => (
              <li key={courseIndex}>
                <a href={course.link} target="_blank" rel="noopener noreferrer">
                  {course.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default Curriculum; 