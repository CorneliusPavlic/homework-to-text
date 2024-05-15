import { useEffect, useRef, useState } from 'react';
import './App.css'

export const Scanner = () => {
  const containerRef = useRef(null);
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const displayFile = useRef(false);
    
  
  useEffect(() => {
    // eslint-disable-next-line no-undef
    const scanner = new jscanify();
    const canvas = document.getElementById('canvas');
    const canvasCtx = canvas.getContext("2d")
    const result = document.getElementById('result');
    const resultCtx = result.getContext("2d");
    const video = document.getElementById('video');
    
    loadOpenCv(() => {
      try{
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
          video.play();
          const intervalPtr = setInterval(() => {
                if(displayFile.current){
                  clearInterval(intervalPtr);
                  const resultImage = scanner.extractPaper(canvas, 500, 647);
                  resultCtx.drawImage(resultImage,0,0, canvas.width, canvas.height);
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
  }, []);


  const handleDisplayFileClick = () => {
    displayFile.current = true;
  }


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
            </div>
          <form>
          <input type='file' id='myFile' name="filename"/>
          </form>
          <button onClick={handleDisplayFileClick}>Looks Good?</button>
        </div>
        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};


export default Scanner;