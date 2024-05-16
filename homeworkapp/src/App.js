import { useEffect, useRef, useState } from 'react';
import {jsPDF} from 'jspdf'
import './App.css'

export const Scanner = () => {
  const containerRef = useRef(null);
  const displayFile = useRef(false);
  const isRunning = useRef(false);
  const currentName = useRef('');
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const [resetEffect, setResetEffect] = useState(0);
  const [formData, setFormData] = useState([]); // Use state to manage FormData
  const [fileNames, setFileNames] = useState([]); // Store the names of the files
  const [fileData, setFileData] = useState([]); // Store the actual file data 


  useEffect(() => {
    // eslint-disable-next-line no-undef
    const scanner = new jscanify();
    const canvas = document.getElementById('canvas');
    const canvasCtx = canvas.getContext("2d")
    const result = document.getElementById('result');
    result.height = '0px'
    const resultCtx = result.getContext("2d");
    const testAgainst = document.getElementById('hiddenImage').src;
    loadOpenCv(() => {
       try{  
         isRunning.current = true;
         const intervalPtr = setInterval(() => {
               if (document.getElementById('hiddenImage').src !== testAgainst){
                  let image = document.getElementById("hiddenImage");
                  if(!image.complete) {
                  setTimeout(()=>{
                        clearInterval(intervalPtr);
                        canvas.width = image.naturalWidth;
                        canvas.height = image.naturalHeight;
                        result.width = image.naturalWidth;
                        result.height = image.naturalHeight;
                        canvasCtx.drawImage(image, 0,0,image.naturalWidth, image.naturalHeight)
                        const resultImage = scanner.extractPaper(canvas, 500, 1000);
                        resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
                        isRunning.current = false;

                      }, 1000);
                  }
                  else {
                    clearInterval(intervalPtr);
                    canvas.width = image.naturalWidth;
                    canvas.height = image.naturalHeight;
                    result.width = image.naturalWidth;
                    result.height = image.naturalHeight;
                    canvasCtx.drawImage(image, 0,0,image.naturalWidth, image.naturalHeight)
                    console.log(canvas.width);
                    const resultImage = scanner.extractPaper(canvas, 500, 1000);
                    resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
                    isRunning.current = false;
                  }
              }
            }, 10);
      }
      catch(err){
        console.log(err);
      }
  });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetEffect]);

  const addAnotherFile = () => {
    // only jpeg is supported by jsPDF
    var imgData = document.getElementById('result').toDataURL("image/jpeg", 1.0);
    setFormData(prevState => [...prevState, imgData]);

    // Create a unique filename (you can modify this logic)
    const filename = currentName.current;
    setFileNames(prevState => [...prevState, filename]);

    // Optionally store the actual image data
    setFileData(prevState => [...prevState, imgData]);

    setResetEffect(resetEffect + 1);
  };

  const handleDisplayVideoSnapshotClick = () => {
    displayFile.current = true;
  };

  const sendToFlask = () => {
    console.log(formData);
  };

  const handleFileUpload = (event) => {
    if(!isRunning.current) setResetEffect(resetEffect + 1);
    setTimeout(()=> {
      const file = event.target.files[0];
      console.log(file)
      if (file.type === 'application/pdf') {
        return;
      }
      currentName.current = file.name;
      document.getElementById('hiddenImage').src = URL.createObjectURL(file);
    }, 50)
  };

  const deleteFile = (index) => {
    // Update formData, fileNames, and fileData by removing the item at the given index
    setFormData(formData.filter((_, i) => i !== index));
    setFileNames(fileNames.filter((_, i) => i !== index));
    setFileData(fileData.filter((_, i) => i !== index));
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
      <div className="scanner-container">
        <div>
          {!loadedOpenCV && (
            <div>
              <h2>Loading OpenCV...</h2>
            </div>
          )}
          <div className='result-canvas-div'>
            <canvas id="canvas"></canvas>
            <canvas id="result"></canvas>
            <img id='hiddenImage' alt=''/>
          </div>
          <form>
            <input type='file' id='myFile' name="filename" onChange={handleFileUpload}/>
          </form>
          <button onClick={addAnotherFile}>Add this File</button>
          <button onClick={sendToFlask}>Send off to super cool AI</button>

          {/* Display the names of the files */}
          <ul>
            {fileNames.map((fileName, index) => (
              <li key={index}>
                {fileName}
                <button onClick={() => deleteFile(index)}>Delete</button>
              </li>
            ))}
          </ul>
        </div>
        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};

export default Scanner