import React, { useEffect, useState } from "react";
import * as XLSX from "xlsx";
//import { useTable, Column, TableInstance } from "react-table";

interface DataPreviewTableProps {
  file: File | null;
  label: string;
}

/**
 * DataPreviewTable reads the first sheet of an uploaded Excel file,
 * displays the first five rows in a table, and provides a toggle
 * to show/hide the preview.
 */
const DataPreviewTable: React.FC<DataPreviewTableProps> = ({ file, label }) => {
  const [data, setData] = useState<any[]>([]);
  const [columns, setColumns] = useState<Column<object>[]>([]);
  const [show, setShow] = useState<boolean>(true);

  useEffect(() => {
    if (!file) {
      setData([]);
      setColumns([]);
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const wb = XLSX.read(new Uint8Array(e.target?.result as ArrayBuffer), {
        type: "array",
      });
      const ws = wb.Sheets[wb.SheetNames[0]];
      const json: any[] = XLSX.utils.sheet_to_json(ws, { raw: false });
      const preview = json.slice(0, 5);
      setData(preview);
      if (preview.length > 0) {
        const cols: Column<object>[] = Object.keys(preview[0]).map((key) => ({
          Header: key,
          accessor: key,
        }));
        setColumns(cols);
      } else {
        setColumns([]);
      }
    };
    reader.readAsArrayBuffer(file);
  }, [file]);

  // Initialize react-table once
  const tableInstance: TableInstance<object> = useTable({ columns, data });
  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    tableInstance;

  if (!file) return null;

  return (
    <div className="data-preview mb-4">
      <div className="d-flex justify-content-between align-items-center">
        <h5>{label} Preview</h5>
        <button
          type="button"
          className="btn btn-link p-0"
          onClick={() => setShow((s) => !s)}
        >
          {show ? "Hide Preview" : "Show Preview"}
        </button>
      </div>

      {show && (
        <>
          {columns.length > 0 ? (
            <table
              {...getTableProps()}
              className="table table-bordered table-sm mt-2"
            >
              <thead>
                {headerGroups.map((headerGroup) => (
                  <tr {...headerGroup.getHeaderGroupProps()}>
                    {headerGroup.headers.map((column) => (
                      <th {...column.getHeaderProps()}>
                        {column.render("Header")}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody {...getTableBodyProps()}>
                {rows.map((row) => {
                  prepareRow(row);
                  return (
                    <tr {...row.getRowProps()}>
                      {row.cells.map((cell) => (
                        <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p className="text-muted">No data to preview.</p>
          )}
        </>
      )}
    </div>
  );
};

export default DataPreviewTable;
