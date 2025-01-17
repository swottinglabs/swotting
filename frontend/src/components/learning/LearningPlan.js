import React from 'react';
import CourseCard from '../courses/CourseCard';
import './LearningPlan.css';

const LearningPlan = ({ learning_plan }) => {
  return (
    <div className="learning-plan">
      <h2 className="learning-plan-title">Learning Plan</h2>
      {learning_plan.learningPlanSteps.map((step, index) => (
        <div key={index} className="learning-plan-step">
          <div className="step-header">
            <span className="step-number">Step {step.step_number}</span>
            <h3 className="step-title">{step.title}</h3>
          </div>
          <p className="step-description">{step.description}</p>
          <div className="courses-scroll-container">
            <div className="courses-horizontal-grid">
              {step.recommended_courses.map((course, courseIndex) => (
                <div key={courseIndex} className="course-card-wrapper">
                  <CourseCard course={course} />
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default LearningPlan; 