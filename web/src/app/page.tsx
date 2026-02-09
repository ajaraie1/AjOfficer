'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function LoginPage() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const router = useRouter();
    const { setAuth } = useAuthStore();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                const token = await authApi.login(email, password);
                localStorage.setItem('token', token.access_token);
                const user = await authApi.getMe();
                setAuth(user, token.access_token);
                router.push('/dashboard');
            } else {
                await authApi.register(email, password, fullName);
                // After registration, login
                const token = await authApi.login(email, password);
                localStorage.setItem('token', token.access_token);
                const user = await authApi.getMe();
                setAuth(user, token.access_token);
                router.push('/dashboard');
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-primary-900">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">IGAMS</h1>
                    <p className="text-slate-400">Intelligent Goal Achievement Management System</p>
                </div>

                <div className="bg-white rounded-2xl shadow-xl p-8">
                    <div className="flex mb-6">
                        <button
                            onClick={() => setIsLogin(true)}
                            className={`flex-1 py-2 text-center rounded-l-lg transition-colors ${isLogin ? 'bg-primary-600 text-white' : 'bg-slate-100 text-slate-600'
                                }`}
                        >
                            Login
                        </button>
                        <button
                            onClick={() => setIsLogin(false)}
                            className={`flex-1 py-2 text-center rounded-r-lg transition-colors ${!isLogin ? 'bg-primary-600 text-white' : 'bg-slate-100 text-slate-600'
                                }`}
                        >
                            Register
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {!isLogin && (
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    required={!isLogin}
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                required
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn btn-primary py-3 disabled:opacity-50"
                        >
                            {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
                        </button>
                    </form>
                </div>

                <p className="text-center text-slate-400 text-sm mt-6">
                    Management Control & Execution System
                </p>
            </div>
        </div>
    );
}
