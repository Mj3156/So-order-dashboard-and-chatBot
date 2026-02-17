'use client';

import React from 'react';

export function Skeleton({ className }: { className?: string }) {
    return (
        <div className={`animate-pulse bg-slate-800/50 rounded ${className}`} />
    );
}

export function KPISkeleton() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
                <div
                    key={i}
                    className="bg-slate-900/50 backdrop-blur-lg rounded-2xl border border-slate-800 p-6 shadow-2xl ring-1 ring-white/5"
                >
                    <div className="flex items-center justify-between mb-4">
                        <Skeleton className="w-16 h-16 rounded-xl" />
                    </div>
                    <Skeleton className="w-24 h-4 mb-2" />
                    <Skeleton className="w-32 h-8" />
                </div>
            ))}
        </div>
    );
}

export function TableSkeleton() {
    return (
        <div className="w-full space-y-4">
            <div className="flex gap-4">
                {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="flex-1 h-10 rounded-lg" />
                ))}
            </div>
            {[...Array(8)].map((_, i) => (
                <div key={i} className="flex gap-4">
                    {[...Array(5)].map((_, j) => (
                        <Skeleton key={j} className="flex-1 h-12 rounded-lg opacity-50" />
                    ))}
                </div>
            ))}
        </div>
    );
}
