import { useEffect, useRef, useState } from 'react';
import {jsPDF} from 'jspdf'
import './App.css'

export const Scanner = () => {
  const containerRef = useRef(null);
  const displayFile = useRef(false);
  const pdf = useRef(new jsPDF());
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const [resetEffect, setResetEffect] = useState(0);
  const [formData, setFormData] = useState([]); // Use state to manage FormData
    
  
  useEffect(() => {
    // eslint-disable-next-line no-undef
    const scanner = new jscanify();
    const canvas = document.getElementById('canvas');
    const canvasCtx = canvas.getContext("2d")
    const result = document.getElementById('result');
    result.height = '0px'
    const resultCtx = result.getContext("2d");
    const video = document.getElementById('video');
    document.getElementById('hiddenImage').src = '';
    const testAgainst = document.getElementById('hiddenImage').src;
    loadOpenCv(() => {
      try{  
        navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
          video.srcObject = stream;
          video.onloadedmetadata = () => {
            video.play();
            const intervalPtr = setInterval(() => {
              if(displayFile.current){
                console.log("bye")
                clearInterval(intervalPtr);
                canvas.width = "640px";
                  canvas.height = "480px";
                  result.width =  "640px";
                  result.height = "480px";
                const resultImage = scanner.extractPaper(canvas, 500, 647);
                resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
              }
              else if (document.getElementById('hiddenImage').src !== testAgainst){
                let image = document.getElementById("hiddenImage");
                if(!image.complete) setTimeout(()=>{
                  clearInterval(intervalPtr);
                  canvas.width = image.naturalWidth;
                  canvas.height = image.naturalHeight;
                  result.width = image.naturalWidth;
                  result.height = image.naturalHeight;
                  canvasCtx.drawImage(image, 0,0,image.naturalWidth, image.naturalHeight)
                  console.log(canvas.width);
                  const resultImage = scanner.extractPaper(canvas, 500, 647);
                  console.log("this should be right after the error")
                  resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
                }, 1000);
                else {
                  clearInterval(intervalPtr);
                  canvas.width = image.naturalWidth;
                  canvas.height = image.naturalHeight;
                  result.width = image.naturalWidth;
                  result.height = image.naturalHeight;
                  canvasCtx.drawImage(image, 0,0,image.naturalWidth, image.naturalHeight)
                  console.log(canvas.width);
                  const resultImage = scanner.extractPaper(canvas, 500, 647);
                  console.log("this should be right after the error")
                  resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
                }
                }
                else{
                canvasCtx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const resultCanvas = scanner.highlightPaper(canvas);
                resultCtx.drawImage(resultCanvas, 0, 0);
                }
              }, 10);
        };
      });}
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
    setResetEffect(resetEffect + 1);
  }

  const handleDisplayVideoSnapshotClick = () => {
    displayFile.current = true;
  }

  const sendToFlask = () => {
    console.log(formData);
  }

  const handleFileUpload = (event) => {
    
    // Get the selected file
    const file = event.target.files[0];
    if (file.type === 'application/pdf'){
        return
    }

    // Display the image (assuming 'hiddenImage' is an <img> tag in your HTML)
    document.getElementById('hiddenImage').src = URL.createObjectURL(file); 
    // Append the image file to FormData
  
  
    // Now you can send formData to your Flask backend 
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
              <video id="video"></video> 
              <canvas id="canvas"></canvas>
              <canvas id="result"></canvas>
              <img id='hiddenImage' alt=''/>
            </div>
          <form>
          <input type='file' id='myFile' name="filename" onChange={handleFileUpload}/>
          </form>
          <button onClick={handleDisplayVideoSnapshotClick}>Looks Good?</button>
          <button onClick={addAnotherFile}>Add this File</button>
          <button onClick={sendToFlask}>Send off to super cool AI</button>
        </div>
        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};


export default Scanner;