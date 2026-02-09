'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { goalsApi, processesApi } from '@/lib/api';
import { Goal } from '@/types';
import { Plus, Target, Calendar, Sparkles, Trash2 } from 'lucide-react';

export default function GoalsPage() {
    const [goals, setGoals] = useState<Goal[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [designingGoalId, setDesigningGoalId] = useState<string | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        purpose: '',
        target_date: '',
    });

    useEffect(() => {
        fetchGoals();
    }, []);

    const fetchGoals = async () => {
        try {
            const data = await goalsApi.list();
            setGoals(data);
        } catch (err) {
            console.error('Error fetching goals:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await goalsApi.create({
                title: formData.title,
                description: formData.description,
                purpose: formData.purpose,
                target_date: formData.target_date || undefined,
            });
            setFormData({ title: '', description: '', purpose: '', target_date: '' });
            setShowForm(false);
            fetchGoals();
        } catch (err) {
            console.error('Error creating goal:', err);
        }
    };

    const handleAutoDesign = async (goalId: string) => {
        setDesigningGoalId(goalId);
        try {
            await processesApi.autoDesign(goalId);
            alert('Processes designed successfully! Check the Processes page.');
        } catch (err) {
            console.error('Error auto-designing processes:', err);
            alert('Error designing processes. Make sure AI is configured.');
        } finally {
            setDesigningGoalId(null);
        }
    };

    const handleDelete = async (goalId: string) => {
        if (!confirm('Are you sure you want to delete this goal?')) return;
        try {
            await goalsApi.delete(goalId);
            fetchGoals();
        } catch (err) {
            console.error('Error deleting goal:', err);
        }
    };

    const handleActivate = async (goalId: string) => {
        try {
            await goalsApi.update(goalId, { status: 'active' });
            fetchGoals();
        } catch (err) {
            console.error('Error activating goal:', err);
        }
    };

    const statusColors = {
        draft: 'badge-info',
        active: 'badge-success',
        in_progress: 'badge-warning',
        completed: 'badge-success',
        paused: 'badge-info',
        cancelled: 'badge-danger',
    };

    return (
        <div className="flex">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                <div className="max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold text-slate-800">Goals</h1>
                            <p className="text-slate-500 mt-1">Define your objectives with clear purpose</p>
                        </div>
                        <button
                            onClick={() => setShowForm(!showForm)}
                            className="btn btn-primary flex items-center gap-2"
                        >
                            <Plus size={18} />
                            New Goal
                        </button>
                    </div>

                    {/* Create Form */}
                    {showForm && (
                        <div className="card mb-8">
                            <h2 className="card-header">Create New Goal</h2>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">
                                        Goal Title *
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.title}
                                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                        placeholder="What do you want to achieve?"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">
                                        Purpose (WHY) *
                                    </label>
                                    <textarea
                                        value={formData.purpose}
                                        onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                        placeholder="Why is this goal important to you?"
                                        rows={3}
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                        placeholder="Additional details..."
                                        rows={2}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">
                                        Target Date
                                    </label>
                                    <input
                                        type="date"
                                        value={formData.target_date}
                                        onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                    />
                                </div>

                                <div className="flex gap-3 pt-2">
                                    <button type="submit" className="btn btn-primary">
                                        Create Goal
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setShowForm(false)}
                                        className="btn btn-secondary"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    {/* Goals List */}
                    {loading ? (
                        <p className="text-slate-500">Loading goals...</p>
                    ) : goals.length === 0 ? (
                        <div className="card text-center py-12">
                            <Target size={48} className="mx-auto text-slate-300 mb-4" />
                            <h3 className="text-lg font-medium text-slate-600 mb-2">No goals yet</h3>
                            <p className="text-slate-500 mb-6">Create your first goal to get started</p>
                            <button onClick={() => setShowForm(true)} className="btn btn-primary">
                                Create a Goal
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {goals.map((goal) => (
                                <div key={goal.id} className="card">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <h3 className="text-lg font-semibold text-slate-800">{goal.title}</h3>
                                                <span className={`badge ${statusColors[goal.status]}`}>
                                                    {goal.status}
                                                </span>
                                            </div>

                                            <p className="text-slate-600 mb-2">
                                                <span className="font-medium text-primary-600">Why:</span> {goal.purpose}
                                            </p>

                                            {goal.description && (
                                                <p className="text-sm text-slate-500 mb-3">{goal.description}</p>
                                            )}

                                            <div className="flex items-center gap-4 text-sm text-slate-500">
                                                {goal.target_date && (
                                                    <span className="flex items-center gap-1">
                                                        <Calendar size={14} />
                                                        Target: {new Date(goal.target_date).toLocaleDateString()}
                                                    </span>
                                                )}
                                                <span>
                                                    Resources: {goal.resources?.length || 0}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            {goal.status === 'draft' && (
                                                <button
                                                    onClick={() => handleActivate(goal.id)}
                                                    className="btn btn-secondary text-sm"
                                                >
                                                    Activate
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleAutoDesign(goal.id)}
                                                disabled={designingGoalId === goal.id}
                                                className="btn btn-primary text-sm flex items-center gap-1"
                                            >
                                                <Sparkles size={14} />
                                                {designingGoalId === goal.id ? 'Designing...' : 'Auto-Design'}
                                            </button>
                                            <button
                                                onClick={() => handleDelete(goal.id)}
                                                className="btn btn-danger text-sm"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
