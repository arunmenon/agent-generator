import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Single call to create crew - original method
export const postCreateCrew = (data: any) => api.post('/meta-agent/create_crew', data);

// New flow-based crew creation
export const postCreateCrewFlow = (data: any) => {
  // Convert to query parameters for GET request
  const params = new URLSearchParams();
  for (const key in data) {
    params.append(key, data[key]);
  }
  return api.post(`/flow/create?${params.toString()}`);
};

// Debug endpoint for flow-based creation
export const postDebugCrewFlow = (data: any) => api.post('/flow/debug', data);

export const getCrews = () => api.get('/crews');
export const getCrewById = (id: string) => api.get(`/crews/${id}`);

export default api;
