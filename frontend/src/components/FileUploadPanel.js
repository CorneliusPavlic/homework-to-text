import React, { useRef, useState, useEffect } from 'react';
import '../styles/FileUploadPanel.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
const FileUploadPanel = ({ files, onUploadComplete, onAddMoreFiles, restoreDeletedItems, setErrors}) => {
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState([]);
  const fileInputRef = useRef(null);
  const prevFilesLengthRef = useRef(0); // Store previous length of files array



  const uploadFile = async (file, index) => {
    if (!file) {
      console.error('No file provided for upload');
      return;
    }
  
    const formData = new FormData();
    formData.append('file', file);
  

    try {
      const response = await fetch('/api/sendFiles', {
        method: 'POST',
        body: formData, 
      });
  
      if (response.ok) {
        const result = await response.json();
        setUploadResults((prev) => [...prev, { fileName: file.name, result }]);
        onUploadComplete(file.name, result); // Notify parent component
        setUploadProgress((prev) => ({ ...prev, [index]: 100 }));
      } else {
        console.error('Upload failed:', response.statusText); 
        setErrors('Upload failed:', response.statusText);
        setUploadProgress((prev) => ({ ...prev, [index]: 0 }));
      }
     } catch (error) {
      console.error('Upload error:', error);
      setErrors('Upload error:', error);
      setUploadProgress((prev) => ({ ...prev, [index]: 0 }));
     }
  };

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);
    onAddMoreFiles(newFiles);
    // uploadFile(newFiles[0], files.length);
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

const deleteFile = (index) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    onAddMoreFiles(newFiles, false);
}
const startUpload = () => {
  const lastIndex = files.length - 1;

  if (lastIndex >= 0) {
    // Initialize progress for the last file
    setUploadProgress((prev) => ({ ...prev, [lastIndex]: 0 }));

    // Upload the last file
    
    uploadFile(files[lastIndex], lastIndex);
  }
};


useEffect(() => {
    if (files.length > prevFilesLengthRef.current) {
      startUpload();
    }
    prevFilesLengthRef.current = files.length; // Update previous length reference
  }, [files]);

  return (
    <div className="file-upload-panel">
      <div className="panel-header">
        <span className="panel-title">Files Uploading</span>
      </div>
      <div className="file-list">
        {files.map((file, index) => (
          <div key={index} className="file-item">
            <img src={URL.createObjectURL(file)} alt={file.name} className="file-thumbnail" onClick={() => restoreDeletedItems(file.name)}/>
            <span className="file-name">{file.name}</span>

            <div className="progress-container">

            <div className="progress-bar">
              <div
                className="progress"
                style={{ width: `${uploadProgress[index] || 0}%` }}
              ></div>
            </div>
            <button
              className="delete-button"
              onClick={() => deleteFile(index)}
            >
              <FontAwesomeIcon icon={faTrash} />
            </button>
            </div>
            <div className="upload-status">
              {uploadProgress[index] === 100 ? "Complete" : "Uploading..."}
            </div>
          </div>
        ))}
      </div>
      <div className="panel-footer">
        <button className="add-more-button" onClick={triggerFileInput}>Add More</button>
        <span className="progress-info">
          {`${Object.values(uploadProgress).filter(progress => progress === 100).length}/${files.length} Files Processed`}
        </span>
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        multiple
      />
    </div>
  );
};

export default FileUploadPanel;