import { useEffect, useRef, useState } from 'react';
import './Scanner.css';

export const Scanner = () => {
  const containerRef = useRef(null);
  const isRunning = useRef(false);
  const currentName = useRef('');
  const currentFile = useRef('');
  const result = useRef(null);
  const resultCtx = useRef(null);
  const image = useRef(null);
  const scanner = useRef(null);
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const [resetEffect, setResetEffect] = useState(0);
  const [fileData, setFormData] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [imgSrc, setImgSrc] = useState('');
  const [data, setData] = useState(''); 
  const [isDarkMode, setIsDarkMode] = useState(false); 
  const [editedData, setEditedData] = useState(''); 
  const [isLoading, setIsLoading] = useState(false); // State for loading animation\
  const [useCentering, setUseCentering] = useState(false);
  const fileInputRef = useRef(null); // Reference for the file input
  

  useEffect(() => {
    console.log(fileData);  // This will log whenever fileData changes
}, [fileData]); 

  const handleFileUpload = (file) => {
    if (!file) return; // Handle case where file is not provided (e.g., drag-and-drop)
    currentName.current = file.name;
    if (file.type === 'application/pdf') {
        currentFile.current = file;
        resultCtx.current.font = '20px serif';
        resultCtx.current.fillText(file.name, 10, 50)
    }
    else if (useCentering === false){
      currentFile.current = file;
      setImgSrc(URL.createObjectURL(file));
    }
    else {
      setImgSrc(URL.createObjectURL(file));
    }
  };
  // Handle file drop
  const handleFileDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    handleFileUpload(file); // Use the same handleFileUpload function
  };

  // Prevent default behavior when dragging over
  const handleDragOver = (event) => {
    event.preventDefault();
  };

  
  // Function to trigger file input click
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };


  const handleTextChange = (event) => {
    setEditedData(event.target.value);
  };
  // Toggle Dark Mode
  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleCentering = () => {
    setUseCentering(!useCentering);
  }

  useEffect(() => {
    document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
  }, [isDarkMode]);

  useEffect(() => {
    loadOpenCv(() => {
      result.current = document.getElementById('result');
      resultCtx.current = result.current.getContext('2d');
      image.current = document.getElementById('hiddenImage');
      // eslint-disable-next-line no-undef
      scanner.current = new jscanify();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (imgSrc === '') return;
    if (document.getElementById('hiddenImage').complete) {
      extractFileFromCanvas();
    } else {
      setTimeout(extractFileFromCanvas, 1000);
    }
  }, [imgSrc]);
  
  const extractFileFromCanvas = () => {
    result.current.width = image.current.naturalWidth;
    result.current.height = image.current.naturalHeight;
    resultCtx.current.drawImage(
      image.current,
      0,
      0,
      image.current.naturalWidth,
      image.current.naturalHeight
    );
    const resultImage = scanner.current.extractPaper(result.current, 500, 1000);
    resultCtx.current.drawImage(resultImage, 0, 0, result.current.width, result.current.height);
    result.current.style.width = '400px';
    result.current.style.height = '500px';
    isRunning.current = false;
  };
  
  const addAnotherFile = () => {
    if (currentFile.current !== '') {
      setFormData((prevState) => [...prevState, currentFile.current]);
      setTimeout(() => {currentFile.current = '';}, 500);
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
  
  // const handleFileUpload = (event) => {
  //   const file = event.target.files[0];
  //   currentName.current = file.name;
  //   setImgSrc(URL.createObjectURL(file));
  // };
  const sendToFlask = async (event) => {
    event.preventDefault();
    setIsLoading(true); // Start loading animation
    const formData = new FormData();
    fileData.forEach((file) => {
      formData.append('file', file);
    });
    console.log(fileData);
    try {
      const response = await fetch('http://localhost:5000/api/sendFiles', {
        mode: 'cors',
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        setIsLoading(false); // Start loading animation
        const data = await response.text();
        console.log(data);
        setData(data);
        setEditedData(data);
        const resultElement = document.getElementById('math');
        resultElement.textContent = data;
      } else {
        setIsLoading(false); // Start loading animation
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  const sendToOpenAI = async () => {
    try {
      setIsLoading(true); // Start loading animation
      const response = await fetch('http://localhost:5000', {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data }),
      });
      if (response.ok) {
        setIsLoading(false); // Start loading animation
        const result = await response.text();
        console.log('Sent to OpenAI successfully:', result);
      } else {
        setIsLoading(false); // Start loading animation
        console.error('Failed to send to OpenAI:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending to OpenAI:', error);
    }
  };

  const sendToGemini = async () => {
    try {
      setIsLoading(true); // Start loading animation
      const response = await fetch('http://localhost:5000', {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data }),
      });
      if (response.ok) {
        setIsLoading(false); // Start loading animation
        const data = await response.text();
        setData(data); 
        setEditedData(data);
        const resultElement = document.getElementById('math');
        resultElement.textContent = data;
        console.log('Sent to Gemini successfully:', result);
      } else {
        setIsLoading(false); // Start loading animation
        console.error('Failed to send to Gemini:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending to Gemini:', error);
    }
  };

  const loadOpenCv = (onComplete) => {
    const isScriptPresent = !!document.getElementById('open-cv');
    if (isScriptPresent || loadedOpenCV) {
      setLoadedOpenCV(true);
      onComplete();
    } else {
      const script = document.createElement('script');
      script.id = 'open-cv';
      script.src = openCvURL;

      script.onload = function () {
        setTimeout(function () {
          onComplete();
        }, 1000);
        setLoadedOpenCV(true);
      };
      document.body.appendChild(script);
    }
  };

  return (
    <>
      <input
        type="checkbox"
        className="dark-mode-toggle"
        id="dark-mode-toggle"
        checked={isDarkMode}
        onChange={toggleDarkMode}
      />
       
      <div className="scanner-container">
        <div>
          {!loadedOpenCV && (
            <div>
              <h2>Loading OpenCV...</h2>
            </div>
          )}

          {isLoading && ( // Show the loading animation if isLoading is true
            <div className="loading-container"> {/* New container for overlay */}
              <div className="lds-ring"><div></div><div></div><div></div><div></div></div>
            </div>
          )}

          <div className="result-canvas-div">
            <canvas id="result"></canvas>
            <img id="hiddenImage" alt="" src={imgSrc} />
          </div>

          <div className="file-upload-area" onDrop={handleFileDrop} onDragOver={handleDragOver} onClick={triggerFileInput}>
            <input type="file" id="myFile" name="filename" ref={fileInputRef} onChange={(event) => handleFileUpload(event.target.files[0])}  hidden /> 
            <span className="file-upload-icon">+</span> 
            <span className="file-upload-text">Drag and drop a file here, or click to upload</span>
          </div>

          <form onSubmit={sendToFlask}>
          </form>
            <div className="button-container">
              <button onClick={addAnotherFile} className="primary-color send-button">
                Add File
              </button>
              <button onClick={sendToFlask} className="primary-color send-button">
                Send to Flask
              </button> 
              <input
              type="checkbox"
              checked={useCentering}
              id='centeringToggle'
              onChange={toggleCentering}
              />
              <label for="centeringToggle">Only select if the image is not scanned</label>
            </div>

          <ul>
            {fileNames.map((fileName, index) => (
              <li key={index}>
                {fileName}
                <button onClick={() => deleteFile(index)} className="secondary-color">Delete</button> 
              </li>
            ))}
          </ul>

          {data && ( // Show the buttons only if data is available
            <>
              <button onClick={sendToOpenAI} className="secondary-color">
                Send to OpenAI
              </button>
              <button onClick={sendToGemini} className="secondary-color">
                Send to Gemini
              </button>
            </>
          )}

        </div>

        <textarea
          id="math"
          className="text-box"
          value={editedData}
          onChange={handleTextChange}
          rows={10}
        ></textarea>

        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};

export default Scanner;