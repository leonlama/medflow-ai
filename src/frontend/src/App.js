// src/frontend/src/App.js
import { useState } from 'react';
import axios from 'axios';

function App() {
  const [data, setData] = useState([]);
  const [transcript, setTranscript] = useState("");

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const path = `sample_data/${file.name}`;
    // Upload to Azure Function storage or use local path
    const { data: json } = await axios.post('/api/CleanData', { input_path: path });
    setData(json);
    const { data: text } = await axios.post('/api/TranscribeAudio', { audio_path: path });
    setTranscript(text.transcript);
  };

  return (
    <div className="p-4">
      <h1>MedFlow AI Demo</h1>
      <input type="file" onChange={handleUpload} />
      <pre>{JSON.stringify(data, null, 2)}</pre>
      <blockquote>{transcript}</blockquote>
      <iframe title="Compliance Dashboard" src="<YOUR_POWERBI_EMBED_URL>" style={{ width:'100%', height:'600px' }}/>
    </div>
  );
}
export default App;
