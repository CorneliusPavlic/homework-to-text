import React, { useState } from 'react';
import '../styles/ResultModal.css'; // Custom styles for the modal

const ResultModal = ({ resultText, onClose }) => {
  const [text, setText] = useState(resultText);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    alert('Text copied to clipboard!');
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2>Edit Result</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          cols={50}
        />
        <div className="modal-actions">
          <button onClick={handleCopy}>Copy Text</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default ResultModal;
