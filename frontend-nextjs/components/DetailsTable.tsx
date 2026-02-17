'use client';

import React, { useRef, useMemo, useState, useEffect, useCallback } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, IDatasource, IGetRowsParams } from 'ag-grid-community';
import { Search } from 'lucide-react';
import { TableSkeleton } from './Skeleton';

interface DetailsTableProps {
    status: string;
    onDataFetch: (page: number, pageSize: number) => Promise<any>;
    loading: boolean;
    searchQuery?: string;
    onRowClick?: (rowData: any) => void;
}

export default function DetailsTable({
    status,
    onDataFetch,
    loading,
    searchQuery,
    onRowClick,
}: DetailsTableProps) {
    const gridRef = useRef<AgGridReact>(null);
    const [totalRows, setTotalRows] = useState(0);
    const [loadedRows, setLoadedRows] = useState(0);
    const [columnDefs, setColumnDefs] = useState<ColDef[]>([]);
    const [isInitializing, setIsInitializing] = useState(true);

    // Default column properties
    const defaultColDef = useMemo<ColDef>(
        () => ({
            flex: 1,
            minWidth: 100,
            sortable: true,
            filter: true,
            resizable: true,
        }),
        []
    );

    // Initialize columns and total count once when status changes
    useEffect(() => {
        let isMounted = true;
        const init = async () => {
            try {
                setIsInitializing(true);
                // Fetch with search to get current query totals
                const result = await onDataFetch(1, 100);

                if (!isMounted) return;

                // If search returned data, use those columns
                if (result.data && result.data.length > 0) {
                    const newColumnDefs = Object.keys(result.data[0]).map((key) => ({
                        field: key,
                        headerName: key,
                        flex: 1,
                        minWidth: 120,
                        resizable: true,
                        sortable: true,
                        filter: true,
                    }));
                    setColumnDefs(newColumnDefs);
                } else if (columnDefs.length === 0) {
                    // Fallback: If search is empty, fetch first row of status (no search) just for headers
                    // We do this via onDataFetch but we can't easily remove search here.
                    // However, if result.total_rows is 0, we still want headers.
                    // For now, let's just use a hardcoded set of common headers if data is empty
                    // OR better: the backend should return columns.
                    // Since I can't easily change the hook, I'll allow columnDefs to be empty
                    // but set isInitializing to false so it doesn't hang.
                }

                setTotalRows(result.total_rows);
                setLoadedRows(result.data.length);
            } catch (error) {
                console.error('Error initializing details table:', error);
            } finally {
                if (isMounted) setIsInitializing(false);
            }
        };

        init();
        return () => { isMounted = false; };
    }, [onDataFetch]); // onDataFetch is stable because of useCallback in Dashboard

    // Stable datasource for subsequent pages
    const datasource: IDatasource = useMemo(() => ({
        getRows: async (params: IGetRowsParams) => {
            // Calculate page (1-indexed)
            const page = Math.floor(params.startRow / 100) + 1;

            try {
                const result = await onDataFetch(page, 100);
                setLoadedRows(params.endRow);
                params.successCallback(result.data, result.total_rows);
            } catch (error) {
                console.error('Error fetching more rows:', error);
                params.failCallback();
            }
        }
    }), [onDataFetch]);

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-semibold text-white">
                        Details for: <span className="text-blue-400">{status}</span>
                    </h3>
                    <p className="text-sm text-gray-400 mt-1 h-5">
                        {isInitializing ? (
                            'Initializing dashboard data...'
                        ) : totalRows > 0 ? (
                            <>
                                Showing up to {Math.min(loadedRows, totalRows).toLocaleString()} of {totalRows.toLocaleString()} rows
                                {loadedRows < totalRows && ' • Scroll down to load more'}
                            </>
                        ) : (
                            'No data found'
                        )}
                    </p>
                </div>
            </div>

            {/* AG Grid Table with Infinite Scroll */}
            <div className="ag-theme-alpine-dark w-full transition-all duration-700 ease-in-out" style={{ height: 600 }}>
                {!isInitializing && (columnDefs.length > 0 || totalRows === 0) ? (
                    <div className="w-full h-full relative">
                        {totalRows === 0 && !isInitializing ? (
                            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800">
                                <Search className="w-12 h-12 text-slate-600 mb-4" />
                                <p className="text-slate-400 text-lg font-semibold">No results found for your search</p>
                                <p className="text-slate-500 text-sm">Try using different keywords or clearing the search</p>
                            </div>
                        ) : null}
                        <AgGridReact
                            ref={gridRef}
                            columnDefs={columnDefs.map(col => ({
                                ...col,
                                cellStyle: (params: any) => {
                                    if (typeof params.value === 'number') {
                                        if (params.value > 100) return { color: '#fca5a5', fontWeight: 'bold' } as any;
                                        if (params.value > 50) return { color: '#fcd34d' } as any;
                                        return { color: '#94a3b8' } as any;
                                    }
                                    return undefined;
                                }
                            }))}
                            defaultColDef={defaultColDef}
                            rowModelType="infinite"
                            datasource={datasource}
                            cacheBlockSize={100}
                            cacheOverflowSize={2}
                            maxConcurrentDatasourceRequests={1}
                            infiniteInitialRowCount={100}
                            maxBlocksInCache={10}
                            animateRows={true}
                            onRowClicked={(event) => onRowClick?.(event.data)}
                            overlayLoadingTemplate={'<span class="ag-overlay-loading-center">Loading more rows...</span>'}
                            suppressNoRowsOverlay={true}
                            rowSelection="single"
                        />
                    </div>
                ) : (
                    <div className="w-full h-full p-4 bg-slate-900/10 rounded-xl border border-slate-800/50">
                        <div className="mb-4 flex items-center gap-2 text-blue-400">
                            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                            <span className="text-xs font-bold uppercase tracking-widest">Wrangling Data...</span>
                        </div>
                        <TableSkeleton />
                    </div>
                )}
            </div>
        </div>
    );
}
