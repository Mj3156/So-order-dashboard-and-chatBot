import axios from 'axios';

const API_BASE_URL = 'http://localhost:8008';

export interface SummaryRow {
    'Store Status': string;
    'Open Qty Pcs': number;
    'Allocated Qty Pcs': number;
    'Picked Qty Pcs': number;
    'Unallocated Qty Pcs': number;
}

export interface DetailsResponse {
    data: any[];
    total_rows: number;
    page: number;
    page_size: number;
    total_pages: number;
    returned_rows: number;
    status: string;
}

export const api = {
    getSummary: async (): Promise<SummaryRow[]> => {
        const response = await axios.get(`${API_BASE_URL}/summary`);
        return response.data;
    },

    getDetails: async (
        status: string,
        page: number = 1,
        pageSize: number = 1000,
        search: string = ""
    ): Promise<DetailsResponse> => {
        const response = await axios.get(
            `${API_BASE_URL}/details/${encodeURIComponent(status)}`,
            {
                params: { page, page_size: pageSize, search },
            }
        );
        return response.data;
    },

    chat: async (query: string, history: { role: string; content: string }[]) => {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            query,
            history
        });
        return response.data;
    }
};
