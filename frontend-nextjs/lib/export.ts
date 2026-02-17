import * as XLSX from 'xlsx';

export const exportToExcel = (data: any[], filename: string) => {
    if (!data || data.length === 0) return;

    // Create worksheet from JSON
    const worksheet = XLSX.utils.json_to_sheet(data);

    // Create workbook and add the worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Data');

    // Generate buffer and trigger download
    XLSX.writeFile(workbook, `${filename}.xlsx`);
};
