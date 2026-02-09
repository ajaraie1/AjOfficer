'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Goal } from '@/types';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    setAuth: (user: User, token: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            setAuth: (user, token) => {
                localStorage.setItem('token', token);
                set({ user, token, isAuthenticated: true });
            },
            logout: () => {
                localStorage.removeItem('token');
                set({ user: null, token: null, isAuthenticated: false });
            },
        }),
        {
            name: 'auth-storage',
        }
    )
);

interface AppState {
    selectedGoal: Goal | null;
    selectedDate: string;
    setSelectedGoal: (goal: Goal | null) => void;
    setSelectedDate: (date: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
    selectedGoal: null,
    selectedDate: new Date().toISOString().split('T')[0],
    setSelectedGoal: (goal) => set({ selectedGoal: goal }),
    setSelectedDate: (date) => set({ selectedDate: date }),
}));
