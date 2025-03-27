import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);

  const handleUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const isAudio = file.type.includes("audio");
    const endpoint = isAudio ? "transcribe" : "clean";

    setLoading(true);
    try {
      const { data } = await axios.post(`http://localhost:7071/api/${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(data);
    } catch (error) {
      setResult({ error: error.response?.data || "Upload failed." });
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
  };

  return (
    <div 
      style={{ 
        padding: '2rem', 
        fontFamily: 'sans-serif',
        border: '2px dashed #ccc',
        borderRadius: '12px',
        backgroundColor: dragging ? '#f0f8ff' : '#fff',
        minHeight: '300px'
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <h1>🧠 MedFlow AI</h1>
      <p>Drag & drop a <strong>lab report (PDF)</strong> or <strong>audio file (WAV)</strong> here, or click below to browse</p>
      <input 
        type="file" 
        onChange={handleFileSelect}
        style={{ marginBottom: '1.5rem' }}
      />
      {loading && <p>Loading...</p>}

      {result && (
        <div style={{ marginTop: '1.5rem' }}>
          {result.transcript && (
            <div>
              <h2>🗣 Transcript</h2>
              <pre>{result.transcript}</pre>
            </div>
          )}

          {result.tables && (
            <div>
              <h2>📄 Extracted Table</h2>
              <table border="1" cellPadding="8">
                <thead>
                  <tr>
                    {result.tables[0].cells.slice(0, result.tables[0].column_count).map((cell, idx) => (
                      <th key={idx}>{cell}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: result.tables[0].row_count - 1 }).map((_, rowIdx) => (
                    <tr key={rowIdx}>
                      {result.tables[0].cells
                        .slice(result.tables[0].column_count * (rowIdx + 1), result.tables[0].column_count * (rowIdx + 2))
                        .map((cell, idx) => (
                          <td key={idx}>{cell}</td>
                        ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {result.error && <p style={{ color: "red" }}>❌ {result.error}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
