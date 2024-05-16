import { useEffect, useRef, useState } from 'react';
import './App.css'

export const Scanner = () => {

  const containerRef = useRef(null);

  //true while Interval is running
  const isRunning = useRef(false);

  //saves name of current uploaded file.
  const currentName = useRef('');
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const [resetEffect, setResetEffect] = useState(0); //used to run useEffect when needed.
  const [formData, setFormData] = useState([]); // Use state to manage FormData
  const [fileNames, setFileNames] = useState([]); // Store the names of the files
  const [fileData, setFileData] = useState([]); // Store the actual file data 


  useEffect(() => {
    //creates new scanner to detect edges of the image.
    // eslint-disable-next-line no-undef
    const scanner = new jscanify();

    //canvas
    const result = document.getElementById('result');
    result.height = '0px'
    //canvas context to draw on.
    const resultCtx = result.getContext("2d");
    //checks to see if there has been a new image uploaded.
    const testAgainst = document.getElementById('hiddenImage').src;

    //loads the open CV library then sets an interval to check if an image has been uploaded. If it has it displays it and aborts the interval.
    loadOpenCv(() => {
         isRunning.current = true;
         const intervalPtr = setInterval(() => {
               if (document.getElementById('hiddenImage').src !== testAgainst){
                  let image = document.getElementById("hiddenImage");
                  if(!image.complete) {
                  setTimeout(()=>{
                      extractFileFromCanvas(intervalPtr,result,resultCtx,image,scanner)
                      }, 1000);
                  }
                  else {
                    extractFileFromCanvas(intervalPtr,result,resultCtx,image,scanner)
                  }
              }
            }, 10);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetEffect]);


  //Stops the interval, sets the canvas to the size of the image, then draws the image on the canvas, extracts the paper from it and draws the result to canvas
  const extractFileFromCanvas = (intervalPtr, result, resultCtx,image, scanner) => {
    clearInterval(intervalPtr);
    result.width = image.naturalWidth;
    result.height = image.naturalHeight;
    resultCtx.drawImage(image, 0,0,image.naturalWidth, image.naturalHeight)
    const resultImage = scanner.extractPaper(result, 500, 1000);
    resultCtx.drawImage(resultImage,0,0, result.width, result.height);
    isRunning.current = false;
  }

  //sets new form and file data when the user adds the file to queue.  
  const addAnotherFile = () => {
    var imgData = document.getElementById('result').toDataURL("image/jpeg", 1.0);
    setFormData(prevState => [...prevState, imgData]);


    const filename = currentName.current;
    setFileNames(prevState => [...prevState, filename]);

    // Optionally store the actual image data
    setFileData(prevState => [...prevState, imgData]);

    setResetEffect(resetEffect + 1);
  };


//Will send the information to the backend for processing.
  const sendToFlask = () => {
    console.log(formData);
  };

   
  //resets the interval if it isn't running, and sets the hidden image to be used by the canvas.
  const handleFileUpload = (event) => {
    if(!isRunning.current) setResetEffect(resetEffect + 1);
    setTimeout(()=> {
      const file = event.target.files[0];
      if (file.type === 'application/pdf') {
        return;
      }
      currentName.current = file.name;
      document.getElementById('hiddenImage').src = URL.createObjectURL(file);
    }, 50)
  };


  //removes file from all relevant places. 
  const deleteFile = (index) => {
    // Update formData, fileNames, and fileData by removing the item at the given index
    setFormData(formData.filter((_, i) => i !== index));
    setFileNames(fileNames.filter((_, i) => i !== index));
    setFileData(fileData.filter((_, i) => i !== index));
  };



//adds openCV script if it doesn't exist, then calls passed function.
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