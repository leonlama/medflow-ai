import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState("");

  const handleUpload = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file ? file.name : "");
  };

  return (
    <div className="page-container">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="block-card">
          <h2>MedFlow AI Demo</h2>
          <input type="file" onChange={handleUpload} />
          <p>{selectedFile || "No file selected"}</p>
        </div>
      ))}
    </div>
  );
}

export default App;
