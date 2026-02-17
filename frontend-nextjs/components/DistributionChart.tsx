'use client';

import React from 'react';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
    Legend
} from 'recharts';
import { SummaryRow } from '@/lib/api';

interface DistributionChartProps {
    data: SummaryRow[];
}

const COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];

export default function DistributionChart({ data }: DistributionChartProps) {
    // Filter out 'Grand Total' and sort to show biggest contributors
    const chartData = data
        .filter(row => row['Store Status'] !== 'Grand Total')
        .map(row => ({
            name: row['Store Status'],
            value: row['Open Qty Pcs']
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 7); // Show top 7 categories

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-xl">
                    <p className="text-slate-200 font-bold mb-1">{payload[0].name}</p>
                    <p className="text-blue-400 font-mono">
                        {payload[0].value.toLocaleString()} Pcs
                    </p>
                    <p className="text-slate-500 text-xs mt-1">
                        {((payload[0].value / chartData.reduce((acc, curr) => acc + curr.value, 0)) * 100).toFixed(1)}% of top statuses
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full h-full min-h-[300px] flex flex-col">
            <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                            animationBegin={0}
                            animationDuration={1500}
                        >
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={COLORS[index % COLORS.length]}
                                    stroke="rgba(255,255,255,0.1)"
                                />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                            formatter={(value) => <span className="text-slate-400 text-xs font-medium">{value}</span>}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
