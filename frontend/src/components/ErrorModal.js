import React, { useState } from 'react';
import '../styles/ResultModal.css'; // Custom styles for the modal

const ErrorModal = ({ errorText, setErrors }) => {
  const [text, setText] = useState(errorText);

  const closeModal = () => {
    setErrors(null);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2>Error:</h2>
        <p>{text}</p>
        <div className="modal-actions">
          <button onClick={closeModal}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default ErrorModal;
