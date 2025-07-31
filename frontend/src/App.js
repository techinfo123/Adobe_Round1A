import React, { useState } from "react";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("API result:", data);
      setResult(data.result.summary);
    } catch (err) {
      alert("Error uploading file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800 px-4 py-10 font-sans">
      <div className="max-w-3xl mx-auto bg-white shadow-xl rounded-xl p-8">
        <h1 className="text-4xl font-bold text-blue-600 mb-6 text-center">
          🧠 LLM Document Analyzer
        </h1>

        <p className="text-center text-gray-600 mb-8">
          Upload your document and get intelligent summaries, language info, and outlines.
        </p>

        <div className="flex justify-center">
          <label className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg cursor-pointer transition duration-200">
            Select File
            <input type="file" className="hidden" onChange={handleUpload} />
          </label>
        </div>

        {loading && (
          <div className="text-center mt-6 text-blue-500 font-medium">
            Processing file...
          </div>
        )}

        {result && (
          <div className="mt-10 border-t pt-6 space-y-4">
            <h2 className="text-2xl font-bold text-gray-700">
              📄 Title: <span className="text-black">{result.title}</span>
            </h2>
            <p className="text-lg">
              🌍 Language: <span className="font-medium">{result.language}</span>
            </p>

            <h3 className="text-xl font-semibold text-gray-700 mt-6">🧾 Outline:</h3>
            <div className="bg-gray-50 p-4 rounded-md border overflow-auto">
              <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(result.outline, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
