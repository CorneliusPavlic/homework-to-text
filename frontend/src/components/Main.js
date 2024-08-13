/* eslint-disable jsx-a11y/anchor-is-valid */
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
  const [imageIndex, setImageIndex] = useState(1); // State to track the current image index
  const totalImages = 16; // Total number of images

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

  const handleDownloadClick = (event) => {
    event.preventDefault();

    // Determine the current image number
    const currentImageNumber = imageIndex;

    // Update the href and download attributes dynamically
    const imageFileName = `image${currentImageNumber}.jpg`;
    const downloadFileName = `sampleImage${currentImageNumber}.jpg`;

    // Create a temporary link element and trigger the download
    const link = document.createElement('a');
    link.href = `/${imageFileName}`;
    link.download = downloadFileName;
    link.click();

    // Increment the image index and reset to 1 if it exceeds totalImages
    setImageIndex((prevIndex) => (prevIndex >= totalImages ? 1 : prevIndex + 1));
  };


  return (
    <main>
      <InstructionItem
        step="1"
        title="Capture"
        description="Take photos of your student's work. A scan of the entire page works best, but a picture will also work."
      >
        <img src={cameraIcon} alt="Camera Icon" style={{ display: 'block', margin: '20px auto' }} />
      </InstructionItem>

      <InstructionItem
        step="2"
        title="Upload"
        description={
        <>
        Upload the photo or file(s) here. Add as many files as you want! Don't have your own files? 
        <a className="download-link" href="#" onClick={handleDownloadClick}> Click Here</a> You'll get a new file to test each time.
        </>}
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
