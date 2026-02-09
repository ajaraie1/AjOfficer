'use client';

import { Process, ProcessStep } from '@/types';
import { CheckCircle2, Circle, Clock, AlertCircle } from 'lucide-react';

interface ProcessFlowProps {
    process: Process;
    currentStepId?: string;
}

export default function ProcessFlow({ process, currentStepId }: ProcessFlowProps) {
    const getStepStatus = (step: ProcessStep, index: number) => {
        if (step.id === currentStepId) return 'current';
        if (!step.is_active) return 'inactive';
        return 'pending';
    };

    const statusStyles = {
        current: 'border-primary-500 bg-primary-50',
        completed: 'border-emerald-500 bg-emerald-50',
        pending: 'border-slate-300 bg-white',
        inactive: 'border-slate-200 bg-slate-50 opacity-50',
    };

    const statusIcons = {
        current: <Clock className="text-primary-500" size={16} />,
        completed: <CheckCircle2 className="text-emerald-500" size={16} />,
        pending: <Circle className="text-slate-400" size={16} />,
        inactive: <AlertCircle className="text-slate-400" size={16} />,
    };

    return (
        <div className="card">
            <div className="card-header flex items-center justify-between">
                <span>{process.name}</span>
                <span className={`badge ${process.status === 'active' ? 'badge-success' : 'badge-info'}`}>
                    {process.status}
                </span>
            </div>

            {process.purpose && (
                <p className="text-sm text-slate-500 mb-4">{process.purpose}</p>
            )}

            <div className="space-y-3">
                {process.steps.map((step, index) => {
                    const status = getStepStatus(step, index);
                    return (
                        <div key={step.id} className="flex gap-3">
                            {/* Connection line */}
                            <div className="flex flex-col items-center">
                                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${statusStyles[status]}`}>
                                    {statusIcons[status]}
                                </div>
                                {index < process.steps.length - 1 && (
                                    <div className="w-0.5 h-full min-h-[20px] bg-slate-200 my-1" />
                                )}
                            </div>

                            {/* Step content */}
                            <div className={`flex-1 p-3 rounded-lg border ${statusStyles[status]}`}>
                                <div className="flex items-center gap-2">
                                    {step.action_verb && (
                                        <span className="text-xs font-medium text-primary-600 uppercase">
                                            {step.action_verb}
                                        </span>
                                    )}
                                    <h4 className="font-medium text-slate-800">{step.name}</h4>
                                </div>

                                {step.description && (
                                    <p className="text-sm text-slate-500 mt-1">{step.description}</p>
                                )}

                                <div className="flex flex-wrap gap-3 mt-2 text-xs text-slate-500">
                                    {step.estimated_duration_minutes && (
                                        <span className="flex items-center gap-1">
                                            <Clock size={12} />
                                            {step.estimated_duration_minutes} min
                                        </span>
                                    )}
                                    {step.quality_criteria && (
                                        <span className="text-primary-600">
                                            Quality: {step.quality_criteria}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
