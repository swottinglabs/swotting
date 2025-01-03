type Course = {
  title: string;
  link: string;
  description: string;
};

export async function searchCourses(query: string): Promise<Course[]> {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Mock course data
  const mockCourses: Course[] = [
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

