import './App.css';
import {createCanvas} from 'canvas';
import {jscanify} from 'jscanify';

function App() {
  const scanner = new jscanify();
  const canvas = createCanvas(500,500);
  const result = createCanvas(500,500);
  const canvasCtx = canvas.getContext("2d");
  const resultCtx = result.getContext("2d");

  navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.srcObject = stream;
    video.onloadedmetadata = () => {
      video.play();
  
      setInterval(() => {
        canvasCtx.drawImage(video, 0, 0);
        const resultCanvas = scanner.highlightPaper(canvas);
        resultCtx.drawImage(resultCanvas, 0, 0);
      }, 10);
    };
  });


  return (
    <div>
    <video id="video"></video>
       <input type="file" id="myFile" name="filename" capture="user"></input>
    </div>
  );
}

export default App;
