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
  const [fileData, setFormData] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [imgSrc, setImgSrc] = useState('');
  const [data, setData] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [editedData, setEditedData] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useCentering, setUseCentering] = useState(false);
  const [progress, setProgress] = useState(0); // State for progress bar
  const fileInputRef = useRef(null);

  //Upond file upload If it is a PDF it writes the name of the file to the canvas, otherwise it displays the image on the canvas
  const handleFileUpload = (file) => {
    if (!file) return;
    currentName.current = file.name;
    if (file.type === 'application/pdf') {
      currentFile.current = file;
      resultCtx.current.font = '20px serif';
      resultCtx.current.fillText(file.name, 10, 50);
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

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleCentering = () => {
    setUseCentering(!useCentering);
  };

  useEffect(() => {
    document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
  }, [isDarkMode]);

  useEffect(() => {
    loadOpenCv(() => {
      // sets up canvases with text on the Canvas, This will be replaced when the user uploads an Image. This is free to be changed.
      result.current = document.getElementById('result');
      resultCtx.current = setupCanvas(result.current);
      image.current = document.getElementById('hiddenImage');
      resultCtx.current.font = '16px serif';
      resultCtx.current.fillText("Welcome to MathEdu a project with the goal to help teachers quickly and efficently grade student's work.", 75, 50);
      resultCtx.current.fillText("To get started upload a file and then select add file, feel free to add as many files as you want. ", 100, 75);
      resultCtx.current.fillText("Whenever you're ready select \"Send to be Processed.\" And wait about 25 seconds per page", 105, 100);
      resultCtx.current.fillText("There is also a built in scanner for images taken on phones or images not scanned,", 120, 125);
      resultCtx.current.fillText("If you are using one of those select the checkbox before adding the file.", 140, 150);
      resultCtx.current.fillText("", 140, 175);
      //eslint has to be disabled if there is no line below you'll get wrong errors. Because jscanify is loaded after launch.
      /* eslint-disable */
      scanner.current = new jscanify();
    });
  }, []);


//Sets the pixel density of the canvas. These values can be tweaked a little but be careful because they can become too sharp.
  const setupCanvas = (canvas) => {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return ctx;
  };

//extracts image from the canvas after the image has been loaded
  useEffect(() => {
    //timeout is needed in case the image takes a while to load
    if (imgSrc === '') return;
    if (document.getElementById('hiddenImage').complete) {
      extractFileFromCanvas();
    } else {
      setTimeout(extractFileFromCanvas, 1000);
    }
  }, [imgSrc]);

  //uses openCV to  extract the document from the image
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
          {!loadedOpenCV && (
            <div>
              <h2>Loading OpenCV...</h2>
            </div>
          )}

          <input
            type="checkbox"
            className="dark-mode-toggle"
            id="dark-mode-toggle"
            checked={isDarkMode}
            onChange={toggleDarkMode}
          />

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
              {/* Add more options as needed */}
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
