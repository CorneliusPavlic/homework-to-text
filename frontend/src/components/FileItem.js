import React from 'react';
import '../styles/FileItem.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faTrash } from '@fortawesome/free-solid-svg-icons';

const FileItem = ({ fileName, onDelete, onView }) => {
  return (
    <div className="fileListItem">
      <span className="file-list-name">{fileName}</span>
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

export default FileItem;
