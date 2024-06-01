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
  const [data, setData] = useState(''); // New state to store the response data

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
    isRunning.current = false;
  };

  const addAnotherFile = () => {
    if (currentFile.current !== '') {
      setFormData((prevState) => [...prevState, currentFile.current]);
      currentFile.current = '';
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

  const sendToFlask = async (event) => {
    event.preventDefault();

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
        const data = await response.text();
        console.log('File uploaded successfully!');
        setData(data); // Save the response data
        const resultElement = document.getElementById('math');
        resultElement.textContent = data;
      } else {
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    currentName.current = file.name;

    if (file.type === 'application/pdf') {
      currentFile.current = file;
    } else {
      setImgSrc(URL.createObjectURL(file));
      console.log(image.current.src);
    }
  };

  const deleteFile = (index) => {
    setFormData(fileData.filter((_, i) => i !== index));
    setFileNames(fileNames.filter((_, i) => i !== index));
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

  // New function to send data to the openAI endpoint
  const sendToOpenAI = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/openAI', {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data }),
      });
      if (response.ok) {
        const result = await response.text();
        console.log('Sent to OpenAI successfully:', result);
      } else {
        console.error('Failed to send to OpenAI:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending to OpenAI:', error);
    }
  };

  // New function to send data to the Gemini endpoint
  const sendToGemini = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/Gemini', {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data }),
      });
      if (response.ok) {
        const result = await response.text();
        console.log('Sent to Gemini successfully:', result);
      } else {
        console.error('Failed to send to Gemini:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending to Gemini:', error);
    }
  };

  return (
    <>
      <div className="scanner-container">
        <div>
          {!loadedOpenCV && (
            <div>
              <h2>Loading OpenCV...</h2>
            </div>
          )}
          <div className="result-canvas-div">
            <canvas id="result"></canvas>
            <img id="hiddenImage" alt="" src={imgSrc} />
          </div>
          <form onSubmit={sendToFlask}>
            <input type="file" id="myFile" name="filename" onChange={handleFileUpload} />
          </form>
          <button onClick={addAnotherFile}>Add this File</button>
          <form />
          <button onClick={sendToFlask}>Test contents</button>
          {/* Display the names of the files */}
          <ul>
            {fileNames.map((fileName, index) => (
              <li key={index}>
                {fileName}
                <button onClick={() => deleteFile(index)}>Delete</button>
              </li>
            ))}
          </ul>
          {/* New buttons to send data to openAI and Gemini endpoints */}
          <button onClick={sendToOpenAI} disabled={!data}>
            Send to OpenAI
          </button>
          <button onClick={sendToGemini} disabled={!data}>
            Send to Gemini
          </button>
        </div>
        <p id="math"></p>
        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};

export default Scanner;
