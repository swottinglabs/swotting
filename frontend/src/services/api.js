const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';


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
    }
}; 