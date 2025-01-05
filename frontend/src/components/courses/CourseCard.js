import React from 'react';
import { BiCertification, BiTime, BiDollar } from 'react-icons/bi';
import './CourseCard.css';

const CourseCard = ({ course }) => {
  const getPriceDisplay = () => {
    if (course.is_free) {
      return (
        <div className="price free" title="Free Course">
          <BiDollar className="price-icon" />
        </div>
      );
    }
    if (course.is_limited_free) {
      return (
        <div className="price trial" title="Trial Available">
          <BiTime className="price-icon" />
        </div>
      );
    }
    return (
      <div className="price paid">
        <span>${course.dollar_price}</span>
      </div>
    );
  };

  return (
    <div className="course-card" onClick={() => window.open(course.url, '_blank')}>
      <div className="course-image">
        <img src={course.platform_thumbnail_url} alt={course.name} />
      </div>
      <div className="course-content">
        <div className="course-main">
          <h3 className="course-title">{course.name}</h3>
          <p className="course-description">{course.short_description}</p>
        </div>
        
        <div className="course-footer">
          <div className="course-stats">
            <div className="stat">
              <span className="stat-label">Duration:</span>
              <span className="stat-value">{course.duration_h}h</span>
            </div>
            <div className="stat">
              <span className="stat-label">Enrolled:</span>
              <span className="stat-value">{course.enrollment_count.toLocaleString()}</span>
            </div>
          </div>
          <div className="course-badges">
            {course.has_certificate && (
              <div className="certificate-badge" title="Certificate Available on Completion">
                <BiCertification />
              </div>
            )}
            {getPriceDisplay()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseCard; 