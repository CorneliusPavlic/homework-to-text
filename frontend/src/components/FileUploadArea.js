import React, { useState, useRef } from 'react';
import '../styles/FileUploadArea.css';
import uploadImage from '../assets/drag-icon.png';
import FileUploadPanel from './FileUploadPanel';

const FileUploadArea = ({ files, setFiles, uploadedFiles, setUploadedFiles, restoreDeletedItems, setErrors }) => {
  const fileInputRef = useRef(null);

  const handleFileDrop = (event) => {
    event.preventDefault();
    const newFiles = Array.from(event.dataTransfer.files);
    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
  };

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);
    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleUploadComplete = (fileName, result) => {
    setUploadedFiles((prev) => [...prev, { fileName, result, visible: true }]);
  };

  const handleAddMoreFiles = (newFiles, keepOldFiles=true) => {
    if(keepOldFiles){
      setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    }
    else {
      setFiles((prevFiles) => [...newFiles]);
    }
  };

  return (
    <div className="file-upload-container">
      {files.length === 0 ? (
        <div
          className="file-upload-area"
          onDrop={handleFileDrop}
          onDragOver={handleDragOver}
          onClick={triggerFileInput}
        >
          <input
            type="file"
            id="myFile"
            name="filename"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            multiple
          />
          <img src={uploadImage} alt="Upload File" className="upload-image" />
        </div>
      ) : (
        <FileUploadPanel
          files={files}
          onUploadComplete={handleUploadComplete}
          onAddMoreFiles={handleAddMoreFiles}
          restoreDeletedItems={restoreDeletedItems}
          setErrors={setErrors}
        />
      )}
    </div>
  );
};

export default FileUploadArea;
