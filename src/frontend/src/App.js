import React, { useState } from 'react';
import axios from 'axios';
import DataTable from './DataTable';

function App() {
  const [rows, setRows] = useState([]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Call Azure Function with hardcoded path
    const { data } = await axios.post(
      "http://localhost:7071/api/CleanData",
      { input_path: "sample_data/test_lab_report.pdf" }
    );

    // Set the cleaned data into state
    setRows(data);
  };

  return (
    <div style={{ margin: '2rem' }}>
      <h1>MedFlow AI Demo</h1>
      <input type="file" onChange={handleUpload} />
      <DataTable rows={rows} />
    </div>
  );
}

export default App;
