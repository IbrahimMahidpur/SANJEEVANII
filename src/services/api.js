import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Vaccine Centers
  getVaccineCenters: async (pincode, date) => {
    const response = await api.post('/api/v1/vaccine-centers', { pincode, date });
    return response.data;
  },

  // LLM Chat
  chat: async (message, conversationHistory = []) => {
    const response = await api.post('/api/v1/llm', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  // Health Check
  healthCheck: async () => {
    const response = await api.get('/api/v1/health');
    return response.data;
  },
};

export default apiClient;
