import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

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
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">🧠 MedFlow AI</h1>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={`border-4 border-dashed ${
          dragActive ? "border-blue-500 bg-blue-100" : "border-gray-400"
        } p-6 text-center rounded-xl transition-all`}
      >
        <p className="mb-2">Drag & drop a <strong>lab report (PDF)</strong> or <strong>audio file (WAV)</strong> here</p>
        <p className="mb-2 text-sm text-gray-500">or click to select a file</p>
        <input
          type="file"
          className="hidden"
          id="fileUpload"
          onChange={handleFileSelect}
        />
        <label
          htmlFor="fileUpload"
          className="cursor-pointer bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          Upload File
        </label>
      </div>

      {loading && <p>Loading...</p>}

      {result && (
        <div className="mt-6">
          {result.transcript && (
            <div>
              <h2 className="text-xl font-semibold mb-2">🗣 Transcript</h2>
              <pre className="bg-white p-4 rounded shadow">{result.transcript}</pre>
            </div>
          )}

          {result.tables && (
            <div>
              <h2 className="text-xl font-semibold mb-2">📄 Extracted Table</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white rounded shadow">
                  <thead>
                    <tr>
                      {result.tables[0].cells.slice(0, result.tables[0].column_count).map((cell, idx) => (
                        <th key={idx} className="border p-2">{cell}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Array.from({ length: result.tables[0].row_count - 1 }).map((_, rowIdx) => (
                      <tr key={rowIdx}>
                        {result.tables[0].cells
                          .slice(result.tables[0].column_count * (rowIdx + 1), result.tables[0].column_count * (rowIdx + 2))
                          .map((cell, idx) => (
                            <td key={idx} className="border p-2">{cell}</td>
                          ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {result.error && <p className="text-red-500">❌ {result.error}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
