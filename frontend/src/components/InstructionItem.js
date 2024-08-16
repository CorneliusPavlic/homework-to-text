import React, { useState } from 'react';
import '../styles/InstructionItem.css';

const InstructionItem = ({ step, title, description, children}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="instruction-item">
      <div className="instruction-header" onClick={toggleOpen}>
        <h2>{step}. {title}</h2>
        <span className={`arrow ${isOpen ? 'up' : 'down'}`}>&#9662;</span>
      </div>
      <p className="description">{description}</p>
      <div
        className="instruction-content"
        style={{ display: isOpen ? 'block' : 'none' }}
        >
        {children}
      </div>

    </div>
  );
};

export default InstructionItem;
