import { useEffect, useRef, useState } from 'react';
import './App.css'

export const Scanner = () => {
  const containerRef = useRef(null);
  const openCvURL = 'https://docs.opencv.org/4.7.0/opencv.js';

  const [loadedOpenCV, setLoadedOpenCV] = useState(false);
  const [selectedImage, setSelectedImage] = useState(undefined);

  useEffect(() => {
    // eslint-disable-next-line no-undef
    const scanner = new jscanify();
    const canvasCtx = document.getElementById('canvas').getContext("2d");
    const resultCtx = document.getElementById('result').getContext("2d");
    const video = document.getElementById('video');
    loadOpenCv(() => {
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
          video.play();
              setInterval(() => {
                canvasCtx.drawImage(video, 500, 500);
                const resultCanvas = scanner.highlightPaper(document.getElementById('canvas'));
                resultCtx.drawImage(resultCanvas, 500, 500);
              }, 10);
        };
      });
  });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedImage]);

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
          <video id="video"></video> 
          <canvas id="canvas"></canvas>
          <canvas id="result"></canvas>
        </div>
        <div ref={containerRef} id="result-container"></div>
      </div>
    </>
  );
};


export default Scanner;