import React from 'react';
import '../styles/ResultItem.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faTrash } from '@fortawesome/free-solid-svg-icons';

const ResultItem = ({ fileName, onDelete, onView }) => {
  return (
    <div className="ResultListItem">
      <span className="Result-list-name">{fileName}</span>
      <div className="icon-Container">
        <button className="icon-button" onClick={onView}>
          <FontAwesomeIcon icon={faEye} />
        </button>
        <button className="icon-button" onClick={onDelete}>
          <FontAwesomeIcon icon={faTrash} />
        </button>
      </div>
    </div>
  );
};

export default ResultItem;
