'use client';

interface ProgressBarProps {
    value: number; // 0-100
    label?: string;
    color?: 'blue' | 'green' | 'yellow' | 'red';
    showValue?: boolean;
}

export default function ProgressBar({
    value,
    label,
    color = 'blue',
    showValue = true
}: ProgressBarProps) {
    const colorStyles = {
        blue: 'bg-primary-500',
        green: 'bg-emerald-500',
        yellow: 'bg-amber-500',
        red: 'bg-red-500',
    };

    const clampedValue = Math.min(100, Math.max(0, value));

    return (
        <div className="w-full">
            {(label || showValue) && (
                <div className="flex justify-between items-center mb-1">
                    {label && <span className="text-sm text-slate-600">{label}</span>}
                    {showValue && <span className="text-sm font-medium text-slate-700">{clampedValue.toFixed(0)}%</span>}
                </div>
            )}
            <div className="progress-bar">
                <div
                    className={`progress-fill ${colorStyles[color]}`}
                    style={{ width: `${clampedValue}%` }}
                />
            </div>
        </div>
    );
}
