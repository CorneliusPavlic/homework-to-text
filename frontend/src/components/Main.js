import React, { useEffect, useState } from 'react';
import InstructionItem from './InstructionItem';
import cameraIcon from '../assets/camera-icon.png';
import FileUploadArea from './FileUploadArea';
import FileList from './FileList';
import ResultModal from './ResultModal';

const Main = () => {
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentResult, setCurrentResult] = useState('');

  const handleFileUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    setFiles([...files, ...uploadedFiles]);
  };

  const handleDeleteFile = (index) => {
    setUploadedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  const handleViewResult = (result) => {
    setCurrentResult(result.result);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };
  return (
    <main>
      <InstructionItem
        step="1"
        title="Capture"
        description="Take photos of your student's work. A photo like this will work best, showing one problem at a time."
      >
        <img src={cameraIcon} alt="Camera Icon" style={{ display: 'block', margin: '20px auto' }} />
      </InstructionItem>

      <InstructionItem
        step="2"
        title="Upload"
        description="Upload the photo or file(s) here. Add as many files as you want!"
      >
        <FileUploadArea  files={files} setFiles={setFiles}  uploadedFiles={uploadedFiles} setUploadedFiles={setUploadedFiles} onFileSelect={handleFileUpload} />
      </InstructionItem>

      <InstructionItem
        step="3"
        title="Organize"
        description="Organize and use processed files."
      >
        <FileList
          uploadedFiles={uploadedFiles}
          onDelete={handleDeleteFile}
          onView={handleViewResult}
        />
      </InstructionItem>

      {isModalOpen && (
        <ResultModal
          resultText={currentResult}
          onClose={closeModal}
        />)}
    </main>
  );
};

export default Main;
