/**
 * @typedef {Object} Course
 * @property {string} title - The title of the course
 * @property {string} link - The URL link to the course
 * @property {string} description - A description of the course
 */

/**
 * Searches for courses based on a query string
 * @param {string} query - The search query
 * @returns {Promise<Course[]>} A promise that resolves to an array of courses
 */
export async function searchCourses(query) {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Mock course data
  const mockCourses = [
    {
      title: "Introduction to " + query,
      link: "https://example.com/intro-" + query.toLowerCase(),
      description: "Learn the basics of " + query,
    },
    {
      title: "Advanced " + query + " Techniques",
      link: "https://example.com/advanced-" + query.toLowerCase(),
      description: "Master advanced concepts in " + query,
    },
    {
      title: query + " for Beginners",
      link: "https://example.com/" + query.toLowerCase() + "-beginners",
      description: "A comprehensive guide to " + query + " for newcomers",
    },
  ];

  return mockCourses;
} 