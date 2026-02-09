'use client';

interface MetricCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
    color?: 'blue' | 'green' | 'yellow' | 'red';
}

export default function MetricCard({
    title,
    value,
    subtitle,
    trend,
    trendValue,
    color = 'blue'
}: MetricCardProps) {
    const colorStyles = {
        blue: 'bg-blue-50 border-blue-100',
        green: 'bg-emerald-50 border-emerald-100',
        yellow: 'bg-amber-50 border-amber-100',
        red: 'bg-red-50 border-red-100',
    };

    const trendColors = {
        up: 'text-emerald-600',
        down: 'text-red-600',
        neutral: 'text-slate-500',
    };

    return (
        <div className={`metric-card ${colorStyles[color]}`}>
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <div className="flex items-baseline gap-2 mt-2">
                <p className="metric-value">{value}</p>
                {trendValue && trend && (
                    <span className={`text-sm font-medium ${trendColors[trend]}`}>
                        {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
                    </span>
                )}
            </div>
            {subtitle && (
                <p className="text-sm text-slate-500 mt-1">{subtitle}</p>
            )}
        </div>
    );
}
