import axios from 'axios';
import type { Goal, Process, DailyLog, Measurement, Improvement, User, AuthToken } from '@/types';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth API
export const authApi = {
    login: async (email: string, password: string): Promise<AuthToken> => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        const { data } = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        return data;
    },
    register: async (email: string, password: string, fullName: string): Promise<User> => {
        const { data } = await api.post('/auth/register', { email, password, full_name: fullName });
        return data;
    },
    getMe: async (): Promise<User> => {
        const { data } = await api.get('/auth/me');
        return data;
    },
};

// Goals API
export const goalsApi = {
    list: async (): Promise<Goal[]> => {
        const { data } = await api.get('/inputs/goals');
        return data;
    },
    get: async (id: string): Promise<Goal> => {
        const { data } = await api.get(`/inputs/goals/${id}`);
        return data;
    },
    create: async (goal: Partial<Goal>): Promise<Goal> => {
        const { data } = await api.post('/inputs/goals', goal);
        return data;
    },
    update: async (id: string, goal: Partial<Goal>): Promise<Goal> => {
        const { data } = await api.patch(`/inputs/goals/${id}`, goal);
        return data;
    },
    delete: async (id: string): Promise<void> => {
        await api.delete(`/inputs/goals/${id}`);
    },
};

// Processes API
export const processesApi = {
    listByGoal: async (goalId: string): Promise<Process[]> => {
        const { data } = await api.get(`/processes/goals/${goalId}/processes`);
        return data;
    },
    get: async (id: string): Promise<Process> => {
        const { data } = await api.get(`/processes/${id}`);
        return data;
    },
    create: async (goalId: string, process: Partial<Process>): Promise<Process> => {
        const { data } = await api.post(`/processes/goals/${goalId}/processes`, process);
        return data;
    },
    autoDesign: async (goalId: string): Promise<any> => {
        const { data } = await api.post(`/ai/goals/${goalId}/auto-design`);
        return data;
    },
};

// Daily Operations API
export const operationsApi = {
    listByDate: async (date: string): Promise<DailyLog[]> => {
        const { data } = await api.get(`/operations/logs?execution_date=${date}`);
        return data;
    },
    create: async (log: Partial<DailyLog>): Promise<DailyLog> => {
        const { data } = await api.post('/operations/logs', log);
        return data;
    },
    start: async (logId: string, actualStart: string): Promise<DailyLog> => {
        const { data } = await api.post(`/operations/logs/${logId}/start`, { actual_start: actualStart });
        return data;
    },
    complete: async (logId: string, completion: any): Promise<DailyLog> => {
        const { data } = await api.post(`/operations/logs/${logId}/complete`, completion);
        return data;
    },
};

// Measurements API
export const measurementsApi = {
    getDaily: async (date: string): Promise<any> => {
        const { data } = await api.get(`/measurements/daily/${date}`);
        return data;
    },
    createDaily: async (date: string): Promise<Measurement> => {
        const { data } = await api.post(`/measurements/daily?measurement_date=${date}`);
        return data;
    },
    getIssues: async (date: string): Promise<any> => {
        const { data } = await api.get(`/measurements/issues/${date}`);
        return data;
    },
};

// Control API
export const controlApi = {
    listImprovements: async (): Promise<Improvement[]> => {
        const { data } = await api.get('/control/improvements');
        return data;
    },
    analyze: async (date: string): Promise<any> => {
        const { data } = await api.get(`/control/analyze?target_date=${date}`);
        return data;
    },
    updateImprovement: async (id: string, update: Partial<Improvement>): Promise<Improvement> => {
        const { data } = await api.patch(`/control/improvements/${id}`, update);
        return data;
    },
};

// AI API
export const aiApi = {
    fullAnalysis: async (date: string): Promise<any> => {
        const { data } = await api.get(`/ai/analyze/${date}`);
        return data;
    },
};

export default api;
