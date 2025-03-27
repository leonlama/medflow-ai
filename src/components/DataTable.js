import React from "react";

const DataTable = ({ rows }) => {
  if (!rows || rows.length === 0) return null;

  const { cells, column_count } = rows[0];
  const header = cells.slice(0, column_count);
  const data = [];

  for (let i = column_count; i < cells.length; i += column_count) {
    data.push(cells.slice(i, i + column_count));
  }

  return (
    <div className="mt-6 overflow-x-auto">
      <table className="min-w-full border border-gray-300 rounded-lg shadow-md">
        <thead>
          <tr className="bg-blue-500 text-white">
            {header.map((cell, i) => (
              <th key={i} className="px-4 py-2 border border-white">
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rIdx) => (
            <tr
              key={rIdx}
              className={rIdx % 2 === 0 ? "bg-white" : "bg-gray-100"}
            >
              {row.map((cell, cIdx) => (
                <td key={cIdx} className="px-4 py-2 border border-gray-300">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;

