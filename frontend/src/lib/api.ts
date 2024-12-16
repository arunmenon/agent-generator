import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Single call to create crew
export const postCreateCrew = (data: any) => api.post('/meta-agent/create_crew', data);

export const getCrews = () => api.get('/crews');
export const getCrewById = (id: string) => api.get(`/crews/${id}`);

export default api;
