import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
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

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🧠 MedFlow AI</h1>
      <p>Upload a <strong>lab report (PDF)</strong> or <strong>audio file (WAV)</strong> to extract information.</p>
      <input type="file" onChange={handleUpload} />
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
