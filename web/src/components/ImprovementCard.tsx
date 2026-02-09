'use client';

import { Improvement } from '@/types';
import {
    Lightbulb,
    Scissors,
    ArrowUpDown,
    Merge,
    Split,
    RefreshCw,
    Zap,
    CheckCircle,
    XCircle,
    Clock
} from 'lucide-react';

interface ImprovementCardProps {
    improvement: Improvement;
    onApprove?: () => void;
    onReject?: () => void;
    onImplement?: () => void;
}

const typeIcons = {
    simplify: Scissors,
    remove: XCircle,
    reorder: ArrowUpDown,
    merge: Merge,
    split: Split,
    replace: RefreshCw,
    automate: Zap,
};

const typeColors = {
    simplify: 'text-blue-600 bg-blue-100',
    remove: 'text-red-600 bg-red-100',
    reorder: 'text-purple-600 bg-purple-100',
    merge: 'text-orange-600 bg-orange-100',
    split: 'text-teal-600 bg-teal-100',
    replace: 'text-amber-600 bg-amber-100',
    automate: 'text-emerald-600 bg-emerald-100',
};

const statusBadges = {
    proposed: 'badge-warning',
    approved: 'badge-info',
    implemented: 'badge-success',
    rejected: 'badge-danger',
};

export default function ImprovementCard({
    improvement,
    onApprove,
    onReject,
    onImplement
}: ImprovementCardProps) {
    const Icon = typeIcons[improvement.improvement_type] || Lightbulb;
    const colorClass = typeColors[improvement.improvement_type] || 'text-slate-600 bg-slate-100';

    return (
        <div className="card">
            <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg ${colorClass}`}>
                    <Icon size={20} />
                </div>

                <div className="flex-1">
                    <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-slate-800">{improvement.title}</h4>
                        <span className={`badge ${statusBadges[improvement.status]}`}>
                            {improvement.status}
                        </span>
                    </div>

                    <p className="text-sm text-slate-600 mt-2">{improvement.description}</p>

                    {improvement.rationale && (
                        <p className="text-sm text-slate-500 mt-2 italic">
                            Reason: {improvement.rationale}
                        </p>
                    )}

                    {/* Expected impact */}
                    <div className="flex flex-wrap gap-4 mt-3 text-sm">
                        {improvement.expected_time_savings && (
                            <div className="flex items-center gap-1 text-blue-600">
                                <Clock size={14} />
                                <span>Save {improvement.expected_time_savings} min</span>
                            </div>
                        )}
                        {improvement.expected_quality_improvement && (
                            <div className="flex items-center gap-1 text-emerald-600">
                                <CheckCircle size={14} />
                                <span>+{(improvement.expected_quality_improvement * 100).toFixed(0)}% quality</span>
                            </div>
                        )}
                        {improvement.expected_effort_reduction && (
                            <div className="flex items-center gap-1 text-amber-600">
                                <Zap size={14} />
                                <span>-{(improvement.expected_effort_reduction * 100).toFixed(0)}% effort</span>
                            </div>
                        )}
                    </div>

                    {/* Actions */}
                    {improvement.status === 'proposed' && (
                        <div className="flex gap-2 mt-4">
                            {onApprove && (
                                <button onClick={onApprove} className="btn btn-primary text-sm">
                                    Approve
                                </button>
                            )}
                            {onReject && (
                                <button onClick={onReject} className="btn btn-secondary text-sm">
                                    Reject
                                </button>
                            )}
                        </div>
                    )}

                    {improvement.status === 'approved' && onImplement && (
                        <button onClick={onImplement} className="btn btn-primary text-sm mt-4">
                            Mark as Implemented
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
