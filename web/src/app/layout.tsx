import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'IGAMS - Intelligent Goal Achievement Management System',
    description: 'Management Control & Execution System for achieving goals with less effort',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="min-h-screen bg-slate-50">
                    {children}
                </div>
            </body>
        </html>
    );
}
