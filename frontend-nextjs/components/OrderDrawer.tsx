'use client';

import React from 'react';
import { X, Clipboard, ExternalLink } from 'lucide-react';

interface OrderDrawerProps {
    order: any | null;
    onClose: () => void;
}

export default function OrderDrawer({ order, onClose }: OrderDrawerProps) {
    if (!order) return null;

    const displayFields = Object.entries(order).filter(([key]) => key !== 'id');

    return (
        <>
            {/* Clickable Backdrop */}
            <div
                className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-[100] animate-fade-in cursor-pointer"
                onClick={onClose}
            />

            {/* Drawer Panel */}
            <div className="fixed inset-y-0 right-0 w-full md:w-[450px] bg-slate-900 border-l border-slate-800 shadow-2xl z-[110] flex flex-col animate-slide-in-right">
                {/* Header */}
                <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 backdrop-blur-xl">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                            <Clipboard className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white tracking-tight">Order Details</h2>
                            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mt-0.5">Summary View</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Scrollable Body */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                    {/* Top Priority Fields */}
                    <div className="bg-slate-800/30 rounded-2xl border border-slate-700/50 p-5 space-y-4 shadow-inner">
                        {displayFields.slice(0, 3).map(([key, value]) => (
                            <div key={key} className="flex flex-col">
                                <span className="text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1">{key}</span>
                                <span className="text-white font-medium text-lg leading-tight">
                                    {value === "" || value === null ? <span className="text-slate-700 italic text-sm">Empty</span> : String(value)}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Grid of Remaining Fields */}
                    <div className="space-y-4">
                        <h3 className="text-slate-400 text-[11px] font-bold uppercase tracking-[0.2em] px-1">All Attributes</h3>
                        <div className="grid grid-cols-1 gap-2.5">
                            {displayFields.slice(3).map(([key, value]) => (
                                <div
                                    key={key}
                                    className="flex items-center justify-between p-3.5 rounded-xl bg-slate-800/10 border border-slate-800/50 hover:bg-slate-800/20 hover:border-slate-700 transition-all group"
                                >
                                    <span className="text-xs text-slate-500 font-semibold uppercase tracking-tight">{key}</span>
                                    <span className="text-sm text-slate-300 font-mono text-right max-w-[200px] truncate group-hover:text-white transition-colors">
                                        {value === "" || value === null ? '-' : String(value)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Fixed Footer */}
                <div className="p-6 border-t border-slate-800 bg-slate-900/80 backdrop-blur-md">
                    <button
                        className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-[0.98] flex items-center justify-center gap-2.5"
                        onClick={() => alert('Detailed reporting module coming soon!')}
                    >
                        <ExternalLink className="w-5 h-5 opacity-80" />
                        <span>Generate Full Report</span>
                    </button>
                </div>
            </div>
        </>
    );
}
