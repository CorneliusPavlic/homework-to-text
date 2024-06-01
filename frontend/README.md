# Homework-to-Text Frontend

This is a react front end that consists of almost entirely one component. The scanner component,  the only other thing is in index.html there is a CDN devlivery of the [jscanify library.](https://colonelparrot.github.io/jscanify/). That needs to remain in the final iteration. jscanify uses the OpenCV library so there is also a loading function for that.

The UseEffect function calls loadCV with the setup for the canvas.

The extractFileFromCanvas function, uses the jscanify library to first draw the image to the canvas, then calls extractPaper which removes the paper from the background and sizes it correctly, then draws that back to the canvas. It's called when the imgSrc variable is updated.

The addAnotherFile function triggers when the user clicks the add file button, and adds the file information to the list of files that will be sent to the backend.

the handleFileUpload function triggers when a file is uploaded and adds the relevant information to the places it needs to go, it doesn't actually do much itself other than set off the interval in the useEffect loop.

the deleteFile function simply removes files and names from the array that is storing them when the user clicks the delete button.

The sendToFlask function triggers when user clicks the Test contents button and sends the contents to the Backend. Once it recieves a response it adds the text contents to the math <p> tag This can easily be changed to accomodate where ever it needs to go.

## As to Front end design

Pretty much anything can be changed for styling and moving components, the important components are the canvas and the form, the image tag is never displayed to no need to style it, It just makes drawing to the canvas easier.

The canvas as of right now sets it's size to the original size of the image, this makes for unpredictable sizing so it may need to be placed within a div to control that or the size of the canvas can be modified just be careful of distortion.
