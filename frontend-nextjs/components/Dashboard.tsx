'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BarChart3, Loader2, ArrowLeft, Search, X, Download } from 'lucide-react';
import SummaryTable from './SummaryTable';
import DetailsTable from './DetailsTable';
import DistributionChart from './DistributionChart';
import { api, SummaryRow, DetailsResponse } from '@/lib/api';
import { KPISkeleton, TableSkeleton } from './Skeleton';
import { exportToExcel } from '@/lib/export';
import OrderDrawer from './OrderDrawer';
import ChatAssistant from './ChatAssistant';

export default function Dashboard() {
    const [summaryData, setSummaryData] = useState<SummaryRow[]>([]);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [selectedOrder, setSelectedOrder] = useState<any | null>(null);

    // Load summary data on mount
    useEffect(() => {
        loadSummary();
    }, []);

    const loadSummary = async () => {
        try {
            setSummaryLoading(true);
            const data = await api.getSummary();
            setSummaryData(data);
        } catch (error) {
            console.error('Error loading summary:', error);
        } finally {
            setSummaryLoading(false);
        }
    };

    const handleStatusClick = (status: string) => {
        setSelectedStatus(status);
    };

    const handleDataFetch = useCallback(async (page: number, pageSize: number) => {
        if (!selectedStatus) return { data: [], total_rows: 0 };

        try {
            const result = await api.getDetails(selectedStatus, page, pageSize, debouncedSearch);
            return result;
        } catch (error) {
            console.error('Error loading details:', error);
            return { data: [], total_rows: 0 };
        }
    }, [selectedStatus, debouncedSearch]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <header className="bg-gray-900/50 backdrop-blur-lg border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-500/10 rounded-lg">
                            <BarChart3 className="w-8 h-8 text-blue-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white">SO Order Ageing Dashboard</h1>
                            <p className="text-gray-400 text-sm mt-1">Sales Order Analytics & Insights</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {selectedStatus ? (
                    <div className="space-y-6 animate-fade-in">
                        {/* Top Bar with Back and Search */}
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <button
                                onClick={() => {
                                    setSelectedStatus(null);
                                    setSearchQuery('');
                                }}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700 transition-all group shadow-lg w-fit"
                            >
                                <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                                Back to Summary
                            </button>

                            <div className="relative flex-1 max-w-md flex gap-2">
                                <button
                                    onClick={async () => {
                                        // For details, we fetch a larger chunk (e.g., first 5000 rows) for the export
                                        const result = await api.getDetails(selectedStatus, 1, 5000, debouncedSearch);
                                        exportToExcel(result.data, `SO_Details_${selectedStatus.replace(/\s/g, '_')}`);
                                    }}
                                    className="flex items-center gap-2 px-4 py-2 bg-emerald-600/20 border border-emerald-500/30 rounded-xl text-emerald-400 hover:bg-emerald-600/30 transition-all font-semibold shadow-lg"
                                    title="Export current view to Excel"
                                >
                                    <Download className="w-5 h-5" />
                                    <span>Export</span>
                                </button>
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <input
                                        type="text"
                                        placeholder="Search Store Name, Region, ID..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && setDebouncedSearch(searchQuery)}
                                        className="w-full pl-10 pr-10 py-2 bg-slate-900/80 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                                    />
                                    {searchQuery && (
                                        <button
                                            onClick={() => {
                                                setSearchQuery('');
                                                setDebouncedSearch('');
                                            }}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-800 rounded-full text-slate-400"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>
                                <button
                                    onClick={() => setDebouncedSearch(searchQuery)}
                                    className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20 active:scale-95"
                                >
                                    Search
                                </button>
                            </div>
                        </div>

                        {/* Search Message */}
                        {debouncedSearch && (
                            <div className="px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400 text-sm animate-fade-in">
                                Showing results for "<span className="font-bold">{debouncedSearch}</span>" in <span className="font-bold">{selectedStatus}</span>
                            </div>
                        )}

                        {/* Details Section */}
                        <section className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-2xl ring-1 ring-white/5">
                            <DetailsTable
                                key={`${selectedStatus}-${debouncedSearch}`}
                                status={selectedStatus}
                                onDataFetch={handleDataFetch}
                                loading={detailsLoading}
                                searchQuery={debouncedSearch}
                                onRowClick={setSelectedOrder}
                            />
                        </section>

                        {/* Order Detail Drawer */}
                        <OrderDrawer
                            order={selectedOrder}
                            onClose={() => setSelectedOrder(null)}
                        />
                    </div>
                ) : (
                    <div className="space-y-8">
                        {/* KPI Cards */}
                        {summaryLoading ? (
                            <KPISkeleton />
                        ) : summaryData.length > 0 && (() => {
                            const grandTotal = summaryData.find(row => row['Store Status'] === 'Grand Total');
                            if (!grandTotal) return null;

                            const kpis = [
                                {
                                    label: 'Total Open Qty',
                                    value: grandTotal['Open Qty Pcs'],
                                    icon: '📦',
                                    color: 'from-blue-500 to-indigo-600',
                                    delay: 'delay-100'
                                },
                                {
                                    label: 'Allocated Qty',
                                    value: grandTotal['Allocated Qty Pcs'],
                                    icon: '✅',
                                    color: 'from-emerald-500 to-teal-600',
                                    delay: 'delay-200'
                                },
                                {
                                    label: 'Picked Qty',
                                    value: grandTotal['Picked Qty Pcs'],
                                    icon: '📤',
                                    color: 'from-violet-500 to-purple-600',
                                    delay: 'delay-300'
                                },
                                {
                                    label: 'Unallocated Qty',
                                    value: grandTotal['Unallocated Qty Pcs'],
                                    icon: '⏳',
                                    color: 'from-orange-500 to-amber-600',
                                    delay: 'delay-400'
                                },
                            ];

                            return (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                    {kpis.map((kpi, index) => (
                                        <div
                                            key={index}
                                            className={`opacity-0 animate-fade-in ${kpi.delay} bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl border border-slate-800 p-6 shadow-2xl hover:border-blue-500/50 transition-all duration-500 hover:scale-[1.02] hover:-translate-y-1 ring-1 ring-white/5`}
                                        >
                                            <div className="flex items-center justify-between mb-4">
                                                <div className={`text-4xl p-3 rounded-xl bg-gradient-to-br ${kpi.color} shadow-lg ring-1 ring-white/20`}>
                                                    {kpi.icon}
                                                </div>
                                            </div>
                                            <h3 className="text-slate-400 text-xs font-bold uppercase letter-spacing-widest mb-2">{kpi.label}</h3>
                                            <p className="text-3xl font-extrabold text-white tracking-tight">
                                                {kpi.value.toLocaleString()}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            );
                        })()}

                        {/* Summary & Chart Section */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Summary Table */}
                            <section className="lg:col-span-2 opacity-0 animate-fade-in delay-300 bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 p-8 shadow-2xl ring-1 ring-white/5">
                                <div className="flex items-center justify-between mb-8">
                                    <div className="space-y-1">
                                        <h2 className="text-2xl font-bold text-white tracking-tight">Store Status Summary</h2>
                                        <p className="text-slate-400 text-sm">Real-time aggregation across all stores</p>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <button
                                            onClick={() => exportToExcel(summaryData, 'SO_Order_Summary')}
                                            className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700 transition-all shadow-lg"
                                        >
                                            <Download className="w-4 h-4" />
                                            <span>Download Summary</span>
                                        </button>
                                        {summaryLoading && (
                                            <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                                        )}
                                    </div>
                                </div>
                                <div className="rounded-xl overflow-hidden border border-slate-800 shadow-inner bg-slate-950/20 p-4 min-h-[400px]">
                                    {summaryLoading ? (
                                        <TableSkeleton />
                                    ) : (
                                        <SummaryTable
                                            data={summaryData}
                                            onRowClick={handleStatusClick}
                                            loading={summaryLoading}
                                        />
                                    )}
                                </div>
                            </section>

                            {/* Status Distribution Chart */}
                            <section className="opacity-0 animate-fade-in delay-400 bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 p-8 shadow-2xl ring-1 ring-white/5 flex flex-col">
                                <div className="space-y-1 mb-8">
                                    <h2 className="text-xl font-bold text-white tracking-tight">Status Distribution</h2>
                                    <p className="text-slate-400 text-sm">Top statuses by Open Qty</p>
                                </div>
                                <div className="flex-1 flex items-center justify-center">
                                    <DistributionChart data={summaryData} />
                                </div>
                            </section>
                        </div>
                    </div>
                )}
            </main>

            {/* AI Chat Assistant */}
            <ChatAssistant />
        </div>
    );
}
