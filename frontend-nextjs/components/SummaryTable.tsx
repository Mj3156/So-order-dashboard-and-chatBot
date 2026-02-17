'use client';

import React, { useRef, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { SummaryRow } from '@/lib/api';

interface SummaryTableProps {
    data: SummaryRow[];
    onRowClick: (status: string) => void;
    loading: boolean;
}

export default function SummaryTable({ data, onRowClick, loading }: SummaryTableProps) {
    const gridRef = useRef<AgGridReact>(null);

    const columnDefs: ColDef[] = useMemo(
        () => [
            {
                field: 'Store Status',
                headerName: 'Store Status',
                flex: 2,
                minWidth: 150,
                pinned: 'left',
                cellStyle: (params) => {
                    const isTotal = params.value === 'Grand Total';
                    return {
                        fontWeight: '700',
                        color: isTotal ? '#60a5fa' : '#f8fafc',
                        background: isTotal ? '#1e293b' : 'transparent',
                    } as any;
                },
            },
            {
                field: 'Open Qty Pcs',
                headerName: 'Open Qty',
                flex: 1,
                minWidth: 120,
                type: 'numericColumn',
                valueFormatter: (params) => params.value?.toLocaleString() || '0',
                cellStyle: (params) => {
                    if (params.data['Store Status'] === 'Grand Total') return undefined;
                    if (params.value > 10000) return { backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5' } as any;
                    if (params.value > 5000) return { backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#fcd34d' } as any;
                    return { color: '#94a3b8' } as any;
                }
            },
            {
                field: 'Allocated Qty Pcs',
                headerName: 'Allocated Qty',
                flex: 1,
                minWidth: 120,
                type: 'numericColumn',
                valueFormatter: (params) => params.value?.toLocaleString() || '0',
            },
            {
                field: 'Picked Qty Pcs',
                headerName: 'Picked Qty',
                flex: 1,
                minWidth: 120,
                type: 'numericColumn',
                valueFormatter: (params) => params.value?.toLocaleString() || '0',
            },
            {
                field: 'Unallocated Qty Pcs',
                headerName: 'Unallocated Qty',
                flex: 1,
                minWidth: 120,
                type: 'numericColumn',
                valueFormatter: (params) => params.value?.toLocaleString() || '0',
                cellStyle: (params) => {
                    if (params.data['Store Status'] === 'Grand Total') return undefined;
                    if (params.value > 1000) return { backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', fontWeight: 'bold' } as any;
                    return { color: '#94a3b8' } as any;
                }
            },
        ],
        []
    );

    const defaultColDef = useMemo<ColDef>(
        () => ({
            sortable: true,
            filter: true,
            resizable: true,
        }),
        []
    );

    const onRowClicked = (event: any) => {
        const status = event.data['Store Status'];
        if (status && status !== 'Grand Total') {
            onRowClick(status);
        }
    };

    return (
        <div className="ag-theme-alpine-dark w-full" style={{ height: 500 }}>
            <AgGridReact
                ref={gridRef}
                rowData={data}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                onRowClicked={onRowClicked}
                rowSelection="single"
                animateRows={true}
                loading={loading}
            />
        </div>
    );
}
