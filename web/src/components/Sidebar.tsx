'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Target,
    GitBranch,
    PlayCircle,
    BarChart3,
    Settings2,
    LogOut
} from 'lucide-react';
import { useAuthStore } from '@/lib/store';

const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/goals', label: 'Goals', icon: Target },
    { href: '/processes', label: 'Processes', icon: GitBranch },
    { href: '/operations', label: 'Daily Operations', icon: PlayCircle },
    { href: '/analytics', label: 'Analytics', icon: BarChart3 },
    { href: '/control', label: 'Control', icon: Settings2 },
];

export default function Sidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuthStore();

    return (
        <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900 text-white flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-slate-800">
                <h1 className="text-xl font-bold">IGAMS</h1>
                <p className="text-xs text-slate-400 mt-1">Management Control System</p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4">
                <ul className="space-y-1">
                    {navItems.map((item) => {
                        const isActive = pathname.startsWith(item.href);
                        const Icon = item.icon;
                        return (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                            ? 'bg-primary-600 text-white'
                                            : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                                        }`}
                                >
                                    <Icon size={20} />
                                    <span>{item.label}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* User section */}
            <div className="p-4 border-t border-slate-800">
                <div className="flex items-center gap-3 px-4 py-2">
                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium">
                        {user?.full_name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{user?.full_name || 'User'}</p>
                        <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                    </div>
                </div>
                <button
                    onClick={logout}
                    className="flex items-center gap-3 px-4 py-2 mt-2 w-full text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-800"
                >
                    <LogOut size={18} />
                    <span className="text-sm">Logout</span>
                </button>
            </div>
        </aside>
    );
}
