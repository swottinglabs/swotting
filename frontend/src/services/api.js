const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

// Test function to demonstrate API usage
export const testGenerateCurriculum = async () => {
    try {
        const testData = {
            desired_skill: "Python Programming",
            current_knowledge: "Beginner programming concepts"
        };
        const response = await api.generateCurriculum(testData);
        console.log('Curriculum Generation Response:', response);
        return response;
    } catch (error) {
        console.error('Error generating curriculum:', error);
        throw error;
    }
};

export const api = {
    async get(endpoint) {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        return response.json();
    },

    async post(endpoint, data) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        return response.json();
    },

    async generateCurriculum(data) {
        const response = await fetch(`${API_URL}/generate-curriculum/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        return response.json();
    }
}; 