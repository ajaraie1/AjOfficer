'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import MetricCard from '@/components/MetricCard';
import ProgressBar from '@/components/ProgressBar';
import { goalsApi, measurementsApi, controlApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { Goal, Improvement } from '@/types';
import { Target, CheckCircle2, Clock, TrendingUp, AlertTriangle } from 'lucide-react';

export default function DashboardPage() {
    const { selectedDate } = useAppStore();
    const [goals, setGoals] = useState<Goal[]>([]);
    const [metrics, setMetrics] = useState<any>(null);
    const [improvements, setImprovements] = useState<Improvement[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [goalsData, metricsData, improvementsData] = await Promise.all([
                    goalsApi.list(),
                    measurementsApi.getDaily(selectedDate),
                    controlApi.listImprovements()
                ]);
                setGoals(goalsData);
                setMetrics(metricsData);
                setImprovements(improvementsData.filter((i: Improvement) => i.status === 'proposed'));
            } catch (err) {
                console.error('Error fetching dashboard data:', err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [selectedDate]);

    const activeGoals = goals.filter(g => g.status === 'active' || g.status === 'in_progress');

    return (
        <div className="flex">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
                        <p className="text-slate-500 mt-1">
                            Focus on process quality, not just task completion
                        </p>
                    </div>

                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <MetricCard
                            title="Execution Accuracy"
                            value={metrics?.execution_accuracy ? `${(metrics.execution_accuracy * 100).toFixed(0)}%` : '--'}
                            subtitle="Planned vs Actual"
                            color="blue"
                        />
                        <MetricCard
                            title="Quality Compliance"
                            value={metrics?.quality_compliance ? `${(metrics.quality_compliance * 100).toFixed(0)}%` : '--'}
                            subtitle="Meeting quality criteria"
                            color="green"
                        />
                        <MetricCard
                            title="Time Deviation"
                            value={metrics?.time_deviation ? `${(metrics.time_deviation * 100).toFixed(0)}%` : '--'}
                            subtitle="Ratio to planned time"
                            color={metrics?.time_deviation > 1.2 ? 'yellow' : 'blue'}
                        />
                        <MetricCard
                            title="Process Efficiency"
                            value={metrics?.process_efficiency ? `${(metrics.process_efficiency * 100).toFixed(0)}%` : '--'}
                            subtitle="Output / Effort ratio"
                            color="green"
                        />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Active Goals */}
                        <div className="lg:col-span-2">
                            <div className="card">
                                <div className="card-header flex items-center gap-2">
                                    <Target size={20} className="text-primary-600" />
                                    Active Goals
                                </div>

                                {loading ? (
                                    <p className="text-slate-500">Loading...</p>
                                ) : activeGoals.length === 0 ? (
                                    <div className="text-center py-8">
                                        <Target size={40} className="mx-auto text-slate-300 mb-3" />
                                        <p className="text-slate-500">No active goals</p>
                                        <a href="/goals" className="btn btn-primary mt-4">
                                            Create a Goal
                                        </a>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {activeGoals.slice(0, 5).map((goal) => (
                                            <div key={goal.id} className="p-4 rounded-lg border border-slate-200 hover:border-primary-300 transition-colors">
                                                <div className="flex items-center justify-between mb-2">
                                                    <h4 className="font-medium text-slate-800">{goal.title}</h4>
                                                    <span className={`badge ${goal.status === 'active' ? 'badge-success' : 'badge-info'}`}>
                                                        {goal.status}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-slate-500 mb-3">{goal.purpose}</p>
                                                <ProgressBar value={50} color="blue" />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Improvement Suggestions */}
                        <div>
                            <div className="card">
                                <div className="card-header flex items-center gap-2">
                                    <TrendingUp size={20} className="text-emerald-600" />
                                    Process Improvements
                                </div>

                                {improvements.length === 0 ? (
                                    <div className="text-center py-6">
                                        <CheckCircle2 size={32} className="mx-auto text-emerald-400 mb-2" />
                                        <p className="text-sm text-slate-500">No pending improvements</p>
                                        <p className="text-xs text-slate-400 mt-1">Your processes are running well</p>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {improvements.slice(0, 3).map((imp) => (
                                            <div key={imp.id} className="p-3 rounded-lg bg-amber-50 border border-amber-100">
                                                <div className="flex items-start gap-2">
                                                    <AlertTriangle size={16} className="text-amber-600 mt-0.5" />
                                                    <div>
                                                        <p className="text-sm font-medium text-slate-700">{imp.title}</p>
                                                        <p className="text-xs text-slate-500 mt-1">{imp.description.slice(0, 100)}...</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                        <a href="/control" className="block text-center text-sm text-primary-600 hover:underline">
                                            View all suggestions →
                                        </a>
                                    </div>
                                )}
                            </div>

                            {/* Today's Summary */}
                            <div className="card mt-6">
                                <div className="card-header flex items-center gap-2">
                                    <Clock size={20} className="text-primary-600" />
                                    Today&apos;s Summary
                                </div>
                                <div className="space-y-3">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-slate-500">Steps completed</span>
                                        <span className="font-medium">{metrics?.raw_data?.completed_steps || 0} / {metrics?.raw_data?.total_steps || 0}</span>
                                    </div>
                                    <ProgressBar
                                        value={metrics?.execution_accuracy ? metrics.execution_accuracy * 100 : 0}
                                        color="green"
                                        showValue={false}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
