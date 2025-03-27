import React from 'react';

function DataTable({ rows }) {
  // If there's no data yet, just say so
  if (!rows || rows.length === 0) {
    return <p>No data found.</p>;
  }

  // Grab the column headers from the first row’s keys
  const columns = Object.keys(rows[0]);

  return (
    <table style={{ borderCollapse: 'collapse', marginTop: '1rem' }}>
      <thead>
        <tr>
          {columns.map(col => (
            <th
              key={col}
              style={{ border: '1px solid #ccc', padding: '8px' }}
            >
              {col}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {columns.map(col => (
              <td
                key={col}
                style={{ border: '1px solid #ccc', padding: '8px' }}
              >
                {row[col]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DataTable;
