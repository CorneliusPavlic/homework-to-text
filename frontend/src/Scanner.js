import { useEffect, useRef, useState } from 'react';
import './Scanner.css';

export const Scanner = () => {
  const containerRef = useRef(null);
  const currentName = useRef('');
  const currentFile = useRef('');
  const result = useRef(null);
  const resultCtx = useRef(null);

  const [fileData, setFormData] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [imgSrc, setImgSrc] = useState('');
  const [data, setData] = useState('');
  const [editedData, setEditedData] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useCentering, setUseCentering] = useState(false);
  const [progress, setProgress] = useState(0); // State for progress bar
  const fileInputRef = useRef(null);

  //Upon file upload If it is a PDF it writes the name of the file to the canvas, otherwise it displays the image on the canvas
  const handleFileUpload = (file) => {
    if (!file) return;
    currentName.current = file.name;
    if (file.type === 'application/pdf') {
      currentFile.current = file;
    } else if (useCentering === false) {
      currentFile.current = file;
      setImgSrc(URL.createObjectURL(file));
    } else {
      setImgSrc(URL.createObjectURL(file));
    }
  };

//Calls handlefile upload with the file that was dropped
  const handleFileDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    handleFileUpload(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleTextChange = (event) => {
    setEditedData(event.target.value);
  };



  const toggleCentering = () => {
    setUseCentering(!useCentering);
  };


  const addAnotherFile = () => {
    if (currentFile.current !== '') {
      setFormData((prevState) => [...prevState, currentFile.current]);
      setTimeout(() => {
        currentFile.current = '';
      }, 500);
    } else {
      document.getElementById('result').toBlob((blob) => {
        setFormData((prevState) => [
          ...prevState,
          new File([blob], currentName.current, { type: 'image/jpeg' }),
          'image/jpeg',
        ]);
      }, 'image/jpeg', 1.0);
    }

    const filename = currentName.current;
    setFileNames((prevState) => [...prevState, filename]);
    resultCtx.current.clearRect(0, 0, result.current.width, result.current.height);
  };

  const deleteFile = (index) => {
    setFormData(fileData.filter((_, i) => i !== index));
    setFileNames(fileNames.filter((_, i) => i !== index));
  };

  const sendToFlask = async (event) => {
    event.preventDefault();
    setIsLoading(true); 
    setProgress(0); // Reset progress
    const formData = new FormData();
    fileData.forEach((file) => {
      formData.append('file', file);
    });

    //These values are just filler values. The server isn't going to repsond with updates so just set it to the average time it takes to process a file.
    const totalTime = 25 * fileData.length; // Total time for progress bar (25s per file)
    const updateInterval = 100; // Update interval in ms
    const totalIntervals = totalTime * 1000 / updateInterval; // Total number of intervals

    let currentProgress = 0;

    const progressTimer = setInterval(() => {
      currentProgress += 100 / totalIntervals;
      setProgress(Math.min(currentProgress, 100)); // Ensure progress does not exceed 100%
    }, updateInterval);

    try {
      const response = await fetch('/api/sendFiles', {
        mode: 'cors',
        method: 'POST',
        body: formData,
      });
      clearInterval(progressTimer); // Clear the interval when the request is done
      if (response.ok) {
        setIsLoading(false); 
        setProgress(100); // Set progress to 100% on success
        const data = await response.text();
        console.log(data);
        setData(data);
        setEditedData(data);
        const resultElement = document.getElementById('math');
        resultElement.textContent = data;
      } else {
        setIsLoading(false); 
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      clearInterval(progressTimer); // Clear the interval on error
      console.error('Upload error:', error);
    }
  };


  const formatForLLM = () => {
    let result = data;
    result = "You are a world class mathematics teacher with a specialty in recognizing children's errors in math problems. You will analyze a problem similar to this 2 (1 / 3) + 7 (1 / 5) (1x5 / 3x5) + (1x3 / 5x3) - (5 / 15) + (3 / 15)= (18 / 15) = 1 (3 / 15) = 1 (1 / 5) and give a separate answer for each problem that highlights the places where the child made a mistake: " + result;
    navigator.clipboard.writeText(result);
    alert('Copied the prompt to your clipboard');
    setData(result);
  };


  const fetchImageAsFile = async (imagePath, fileName) => {
    const response = await fetch(imagePath);
    const blob = await response.blob();
    const file = new File([blob], fileName, { type: blob.type });
    return file;
  };


  const handleDropdownChange = async (event) => {
    const selectedValue = event.target.value;
    if (selectedValue) {
      const imagePath = `/image${selectedValue}.jpg`; // Assuming images are named image1.jpg, image2.jpg, etc.
      const fileName = `image(${selectedValue}).jpg`;
      const file = await fetchImageAsFile(imagePath, fileName);
      setImgSrc(URL.createObjectURL(file));
      currentFile.current = file;
      currentName.current = fileName;
    };
  }
  return (
    <>
      <div className="scanner-container">
        <div>

          {isLoading && ( // Show the loading animation if isLoading is true
            <div className="loading-container">
              <div className="loading-holder">
                <p>Loading: {parseInt(progress)}% done</p>
                <div className="loading-bar" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

          <div className="result-canvas-div">
            <canvas id="result"></canvas>
            <img id="hiddenImage" alt="" src={imgSrc} />
          </div>

          <div className="file-upload-area" onDrop={handleFileDrop} onDragOver={handleDragOver} onClick={triggerFileInput}>
            <input type="file" id="myFile" name="filename" ref={fileInputRef} onChange={(event) => handleFileUpload(event.target.files[0])} hidden />
            <span className="file-upload-icon">+</span>
            <span className="file-upload-text">Drag and drop a file here, click to upload, or select an image from the dropdown below</span>
          </div>
          <div>
            <label htmlFor="imageDropdown">Select an Image: </label>
            <select id="imageDropdown" onChange={handleDropdownChange} className=" primary-color dropdown">
              <option value="">--Select an Image--</option>
              <option value="1">Image 1</option>
              <option value="2">Image 2</option>
              <option value="3">Image 3</option>
              <option value="4">Image 4</option>
              <option value="5">Image 5</option>
              <option value="6">Image 6</option>
              <option value="7">Image 7</option>
              <option value="8">Image 8</option>
              <option value="9">Image 9</option>
              <option value="10">Image 10</option>
              <option value="11">Image 11</option>
              <option value="12">Image 12</option>
              <option value="13">Image 13</option>
              <option value="14">Image 14</option>
              <option value="15">Image 15</option>
              <option value="16">Image 16</option>
            </select>
          </div>

          <form onSubmit={sendToFlask}></form>
          <div className="button-container">
            <button onClick={addAnotherFile} className="primary-color send-button">
              Add File
            </button>
            <button onClick={sendToFlask} className="primary-color send-button">
              Send to be Processed
            </button>
            <label className="primary-color send-button">
              <input type="checkbox" checked={useCentering} id="centeringToggle" onChange={toggleCentering} />
              <span>Only select if the file is from a picture (not scanned)&nbsp;&nbsp;</span>
            </label>
          </div>


          <ul>
            {fileNames.map((fileName, index) => (
              <li key={index}>
                {fileName}
                <button onClick={() => deleteFile(index)} className="secondary-color">Delete</button>
              </li>
            ))}
          </ul>

          {data && (
            <>
              <button onClick={formatForLLM} className="secondary-color">
                Get Format For LLM
              </button>
            </>
          )}
        </div>

        <textarea id="math" className="text-box" value={editedData} onChange={handleTextChange} rows={10}></textarea>
        <div ref={containerRef} id="result-container"></div>
      </div>

      <img src="/KentLogo.png" alt="Kent State University Logo" className="top-right-image" />
    </>
  );
};

export default Scanner;
