# Homework to text Back End

This is just a simple backend, it is currently configured to handle calls from localhost:3000, The default port of the React server. It then saves the images as a file in the images folder, If it is a pdf it saves each page as an image. Then iterates over them calling a gemini api prompt on each image. This is not the intended funcitonality of the final product. Eventually it will call an OCR that was developed for the purpose as the Gemini vision is not very accurate. Any modification of the files can easily be added before they are sent to the OCR.
