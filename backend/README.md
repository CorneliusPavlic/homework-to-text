# Homework to text Back End

This backend essentially just takes images from the front end and performs the following on them. with the make_prediction function. All mentioned functions can be found in functions.py and the model can be swapped for any PaddleOCR trained model.


It starts by loading the image of the homework sheet into openCV. Then uses the findContours function to find each of the individual numbers/characters. After that It performs a series of calculations to merge the bounding boxes of the contours that are close together. This continues until you have several large bounding boxes that surround each problem. In some cases it will not merge all necessary boxes and so there is a helper function that will merge boxes that are too small and are within a set distance of each other.  See image #1 This is handled by the segment_problems function

Then I do roughly the same thing on the image but with a much smaller merging radius, resulting in a much larger amount of bounding boxes, See image #2 This is handled by the segment_fractions function

Next the bounding boxes of the problems returned from segment_problems are sorted so that the top left then top right and so on to the bottom are in order, and the fraction bounding boxes are placed in their corresponding problem bounding box. Essentially ordering them so that they each go with their respective problem. This is handled by the bound_equations function.

The images are then cropped and resized while maintaining their aspect ratio by adding white space where necessary.  This is handled by the crop_and_resize function

Then if the image is a fraction it is split into a top half and a bottom half. This is done with openCV contours again and some math. Essentially it selects the images with contours that have a bar in the middle to split on and then splits them there, if they don't have a bar it checks for = signs and splits them (There were issues with the PaddleOCR detecting both = and - signs so splitting the = signs is necessary for a later step.) 

Finally, it runs over all of the images checking for aspect ratios that resemble - signs, and labels those as - signs. And then runs the rest through the PaddleOCR recognizer it is important to note that PaddleOCR is not performing the job of an OCR that is done with the openCV steps labeled above. PaddleOCR is only being used for it's recognizer that was specifically trained on a real dataset of images of handwriting. 

The results from the recognizer are pieced together and common errors are replaced. And the result is returned 
