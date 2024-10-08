import cv2
import numpy as np
import math
import re
from paddleocr import PaddleOCR

from pyimagesearch import transform
from pyimagesearch import imutils
from scipy.spatial import distance as dist
from matplotlib.patches import Polygon
import polygon_interacter as poly_i
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import cv2
from pylsd.lsd import lsd

import argparse
import os
#returns the area of a box with the format top left corner, bottom right corner.
def box_area(box):
    return (box[1][0] - box[0][0]) * (box[1][1] - box[0][1])



def combine_two_closest_boxes(mergable_boxes, distance_for_merge=400):
    if(mergable_boxes == []): return None, None, None
    for i, box in enumerate(mergable_boxes):
        shortest_distance = (10000000, None)
        for j, destination in enumerate(mergable_boxes):
            if j != i:  # Avoid comparing the box with itself
                distance = distance_between_boxes(box, destination)
                if 0 < distance < distance_for_merge and distance < shortest_distance[0]:
                    shortest_distance = (distance, j)
        if shortest_distance[1] is not None:
            return merge_boxes(box, mergable_boxes[shortest_distance[1]]), i, shortest_distance[1]
    return None, None, None  # No mergeable pair found

def distance_between_boxes(p1, p2):
    return math.sqrt((p2[0][0] - p1[0][0])**2 + (p2[0][1] - p1[0][1])**2)

def getAllOverlaps(boxes, bounds, index):
    overlaps = []
    for a in range(len(boxes)):
        if a != index:
            width = boxes[a][1][1] - boxes[a][0][1]
            if width > 100:
                continue
            if overlap(bounds, boxes[a]):
                overlaps.append(a)
    return overlaps

def medianCanny(img, thresh1, thresh2):
    median = np.median(img)
    img = cv2.Canny(img, int(thresh1 * median), int(thresh2 * median))
    return img

def get_xs(roi):
    return roi[1][0][1], roi[1][1][1]

def get_ys(roi):
    return roi[1][0][0], roi[1][1][0]


def merge_boxes(box1, box2):
    return [[min(box1[0][0], box2[0][0]), min(box1[0][1], box2[0][1])], 
            [max(box1[1][0], box2[1][0]), max(box1[1][1], box2[1][1])]]

def overlap(source, target):
    # Unpack points
    tl1, br1 = source
    tl2, br2 = target

    # Check horizontal and vertical overlap
    if tl1[0] >= br2[0] or tl2[0] >= br1[0]:
        return False
    if tl1[1] >= br2[1] or tl2[1] >= br1[1]:
        return False
    return True

def tup(point):
    return (point[0], point[1])



""" One of the major functions, This function takes in the path of the image as input and returns bounding boxes for the problems in the image. It does this by using the following steps:
1. Read the image and convert it to grayscale.
2. Detect Contours
3. Systematically merge bounding boxes around those Contours. 
4. Merge boxes that are close and didn't get a chance to merge. 
5. remove boxes that are too small.

Changeable Parameters: 
    path: just path to image. Or can be passed a numpy array of the image.

    merge_margin_vertical: During the merging phase this is how far the box will be expanded vertically. making this smaller will create more boxes. Making it bigger will reduce the amount of boxes. 

    merge_margin_horizontal: During the merging phase this is how far the box will be expanded horizontally. making this smaller will create more boxes. Making it bigger will reduce the amount of boxes.

    distance_for_final_merge: This is the distance between two boxes that will be merged in the final merge phase make it bigger if you want things on opposite sides of the page to merge.

    minimum_box_size: This is the minimum size of a box that will be returned. Make it smaller if you're not seeing the boxes you would expect.
    debug: will write the image to "SegmentProblemsDebug.png", And draw bounding boxes around the problems. Will slow down the function slightly so make sure to turn it off for production
 """
def segment_problems(path, merge_margin_vertical=70,  merge_margin_horizontal=60, distance_for_final_merge=400, minimum_box_size=200, debug=False):
    if isinstance(path,np.ndarray):
        img = path
    else:
        img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh_binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = cv2.cvtColor(thresh_binary, cv2.COLOR_GRAY2BGR)
    orig = np.copy(img);
    blue, green, red = cv2.split(img)
    blue_edges = medianCanny(blue, 0, 1)
    green_edges = medianCanny(green, 0, 1)
    red_edges = medianCanny(red, 0, 1)
    edges = blue_edges | green_edges | red_edges
    contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    boxes = []; # each element is [[top-left], [bottom-right]];
    hierarchy = hierarchy[0]
    for component in zip(contours, hierarchy):
        currentContour = component[0]
        currentHierarchy = component[1]
        x,y,w,h = cv2.boundingRect(currentContour)
        if currentHierarchy[3] < 0:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
            boxes.append([[x,y], [x+w, y+h]])
    filtered = []
    max_area = 5000
    for box in boxes:
        w = box[1][0] - box[0][0]
        h = box[1][1] - box[0][1]
        if w < 5: continue
        if w*h < max_area:
            filtered.append(box)
    boxes = filtered
    # this is gonna take a long time
    finished = False
    highlight = [[0,0], [1,1]]
    points = [[[0,0]]]
    while not finished:
        # set end con
        finished = True

        # loop through boxes
        index = len(boxes) - 1
        while index >= 0:
            # grab current box
            curr = boxes[index]
            # add margin
            tl = curr[0][:]
            br = curr[1][:]
            tl[0] -= merge_margin_horizontal
            tl[1] -= merge_margin_vertical
            br[0] += merge_margin_horizontal
            br[1] += merge_margin_vertical

            # get matching boxes
            overlaps = getAllOverlaps(boxes, [tl, br], index)
            
            # check if empty
            if len(overlaps) > 0:
                # combine boxes
                # convert to a contour
                con = [];
                overlaps.append(index);
                for ind in overlaps:
                    tl, br = boxes[ind];
                    con.append([tl]);
                    con.append([br]);
                con = np.array(con);

                # get bounding rect
                x,y,w,h = cv2.boundingRect(con);

                # stop growing
                w -= 1;
                h -= 1;
                merged = [[x,y], [x+w, y+h]];

                # highlights
                highlight = merged[:];
                points = con;

                # remove boxes from list
                overlaps.sort(reverse = True);
                for ind in overlaps:
                    del boxes[ind];
                boxes.append(merged);

                # set flag
                finished = False;
                break;

            # increment
            index -= 1;

    copy = np.copy(orig);
    mergable_boxes = []
    big_boxes = []
    for box in boxes: 
        if box_area(box) < 300000:
            mergable_boxes.append(box)
        else: 
            big_boxes.append(box)
    flag = True
    while flag == True:
        new_box, i, j = combine_two_closest_boxes(mergable_boxes, distance_for_final_merge)
        if(new_box == None): flag = False
        else: 
            mergable_boxes.pop(i)
            mergable_boxes.pop(j-1)
            mergable_boxes.append(new_box)


    boxes = big_boxes + mergable_boxes


    bounded_problems = []
    for box in boxes:
        if (box[1][1] - box[0][1]) * (box[1][0] - box[0][0]) < minimum_box_size: continue
        bounded_problems.append(([box[0][1], box[0][0]], [box[1][1], box[1][0]]))
        if debug == True:
            cv2.rectangle(copy, tup(box[0]), tup(box[1]), (0,200,0), 3);
    
    if debug == True:
        cv2.imwrite("SegmentProblemsDebug.png", copy)
    return bounded_problems

""" One of the major functions, This function takes in the path of the image as input and returns bounding boxes for the problems in the image. It does this by using the following steps:
1. Read the image and convert it to grayscale.
2. Detect Contours
3. Systematically merge bounding boxes around those Contours. 
4. remove boxes that are too small.

Changeable Parameters: 
    path: just path to image. Or can be passed a numpy array of the image.

    merge_margin_vertical: During the merging phase this is how far the box will be expanded vertically. making this smaller will create more boxes. Making it bigger will reduce the amount of boxes. 

    merge_margin_horizontal: During the merging phase this is how far the box will be expanded horizontally. making this smaller will create more boxes. Making it bigger will reduce the amount of boxes.
    
    area_for_final_purge: Removes boxes that have areas that suggest they are not a fraction or symbol if they also do not pass the aspect_ratio for final purge test. be careful adjusting this it can cause you to remove symbols.

    aspect_ratio_for_final_purge: Removes boxes that have aspect ratios that along with their area suggest they are not a fraction or symbol. be careful adjusting this it can cause you to remove symbols.
    
    debug: will write the image to "SegmentFractionsDebug.png", And draw bounding boxes around the problems. Will slow down the function slightly so make sure to turn it off for production
 """
def segment_fractions(path, merge_margin_vertical=30, merge_margin_horizontal=1, area_for_final_purge=400, aspect_ratio_for_final_purge=0.8, debug=False):
    if isinstance(path,np.ndarray):
        img = path
    else:
        img = cv2.imread(path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    dilated_lines = cv2.dilate(detected_lines, horizontal_kernel, iterations=1)
    processed_image = cv2.subtract(binary, dilated_lines)
    img = cv2.bitwise_not(processed_image)
    ret, thresh_binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = cv2.cvtColor(thresh_binary, cv2.COLOR_GRAY2BGR)

    orig = np.copy(img);
    blue, green, red = cv2.split(img)
    blue_edges = medianCanny(blue, 0, 1)
    green_edges = medianCanny(green, 0, 1)
    red_edges = medianCanny(red, 0, 1)
    edges = blue_edges | green_edges | red_edges
    contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    # go through the contours and save the box edges
    boxes = []; # each element is [[top-left], [bottom-right]];
    hierarchy = hierarchy[0]
    for component in zip(contours, hierarchy):
        currentContour = component[0]
        currentHierarchy = component[1]
        x,y,w,h = cv2.boundingRect(currentContour)
        if currentHierarchy[3] < 0:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
            boxes.append([[x,y], [x+w, y+h]])

    # filter out excessively large boxes
    filtered = []
    max_area = 4000
    for box in boxes:
        w = box[1][0] - box[0][0]
        h = box[1][1] - box[0][1]
        if w*h < max_area:
            filtered.append(box)
    boxes = filtered

    # this is gonna take a long time
    finished = False
    highlight = [[0,0], [1,1]]
    points = [[[0,0]]]
    while not finished:
        # set end con
        finished = True
        # loop through boxes
        index = len(boxes) - 1
        while index >= 0:
            # grab current box
            curr = boxes[index]
            # add margin
            tl = curr[0][:]
            br = curr[1][:]
            tl[0] -= merge_margin_horizontal
            tl[1] -= merge_margin_vertical
            br[0] += merge_margin_horizontal
            br[1] += merge_margin_vertical

            # get matching boxes
            overlaps = getAllOverlaps(boxes, [tl, br], index)
            
            # check if empty
            if len(overlaps) > 0:
                # combine boxes
                # convert to a contour
                con = [];
                overlaps.append(index);
                for ind in overlaps:
                    tl, br = boxes[ind];
                    con.append([tl]);
                    con.append([br]);
                con = np.array(con);

                # get bounding rect
                x,y,w,h = cv2.boundingRect(con);

                # stop growing
                w -= 1;
                h -= 1;
                merged = [[x,y], [x+w, y+h]];

                # highlights
                highlight = merged[:];
                points = con;

                # remove boxes from list
                overlaps.sort(reverse = True);
                for ind in overlaps:
                    del boxes[ind];
                boxes.append(merged);

                # set flag
                finished = False;
                break;

            # increment
            index -= 1;

    # show finalr
    roi = []
    copy = np.copy(orig);
    for box in boxes:
        area = (box[1][1] - box[0][1]) * (box[1][0] - box[0][0])
        if area < 100 or (area < area_for_final_purge and calculate_aspect_ratio(box) < aspect_ratio_for_final_purge): continue
        if debug == True:
            cv2.rectangle(copy, tup(box[0]), tup(box[1]), (0,200,0), 5);
        roi.append([copy[box[0][1]:box[1][1],box[0][0]:box[1][0]], [[box[0][1], box[0][0]], [box[1][1], box[1][0]]]])

    if debug == True:
        cv2.imwrite("SegmentFractionsDebug.png", copy)
    return roi 

def calculate_aspect_ratio(box):
    # Calculate width and height of the box
    width = abs(box[1][0] - box[0][0])
    height = abs(box[1][1] - box[0][1])
    
    # Avoid division by zero
    if height == 0:
        return "Height is zero, aspect ratio undefined"
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    
    return aspect_ratio


""" One of the major functions, This functions takes the bounding equations and roi from fractions and sorts them by logical order. You can change the sorting logic if you want to. Annotated by comments"""
def bound_equations(bounded_problems, roi):
    #sorts bounded problems by top left Y then top left X
    bounded_problems = sorted(bounded_problems, key=lambda x: (x[0][0], x[0][1]))
    bounded_equations = []
    for bounded_problem in bounded_problems:
        eligible_equations = []
        for r in roi:
            x_near, x_far = get_xs(r)
            midpoint_x = x_far - ((x_far - x_near)/2)
            y_near, y_far = get_ys(r)
            midpoint_y = y_far - ((y_far - y_near)/2) 
            if((midpoint_x > bounded_problem[0][1] and midpoint_x < bounded_problem[1][1]) and (midpoint_y > bounded_problem[0][0] and midpoint_y < bounded_problem[1][0])):
                eligible_equations.append(r)
        bounded_equations.append(eligible_equations)

    for box_index, box in enumerate(bounded_equations):
        #sorts the equations by the midpoint of the x and y coordinates multiplies the x and y with a bias towards the Y. 
        bounded_equations[box_index] = sorted(box, key=lambda item: (
                                                                     ((item[1][1][1] - ((item[1][1][1] - item[1][0][1])/2))*0.8) +
                                                                     (item[1][1][0] - ((item[1][1][0] - item[1][0][0])/2))
                                                                     ), reverse=False)
    return bounded_equations


def resize_with_aspect_ratio(image, target_size=(56, 56), color=(255, 255, 255)):
    # Get the dimensions of the image
    h, w = image.shape[:2]
    # Determine the scale factor and the new size preserving the aspect ratio
    scale = min(target_size[0] / w, target_size[1] / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    if new_w == 0 or new_h ==0: 
        return None
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create a new image with the target size and fill it with the background color
    new_image = np.full((target_size[1], target_size[0], 3), color, dtype=np.uint8)

    # Calculate the position to place the resized image
    x_offset = (target_size[0] - new_w) // 2
    y_offset = (target_size[1] - new_h) // 2

    # Place the resized image on the center of the new image
    new_image[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_image

    return new_image


"""One of the major functions just crops and resizes them all."""
def crop_and_resize(bounded_equations):
    cropped_and_resized = []
    for box in bounded_equations:
        for equation in box:
            test = resize_with_aspect_ratio(equation[0])
            if test is not None:
                test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
                cropped_and_resized.append(test)
    return cropped_and_resized

def calculate_contour_distance(contour1, contour2): 
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    c_x1 = x1 + w1/2
    c_y1 = y1 + h1/2

    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    c_x2 = x2 + w2/2
    c_y2 = y2 + h2/2

    return max(abs(c_x1 - c_x2) - (w1 + w2)/2, abs(c_y1 - c_y2) - (h1 + h2)/2)

def merge_contours(contour1, contour2):
    return np.concatenate((contour1, contour2), axis=0)

def agglomerative_cluster(contours, threshold_distance=40.0):
    current_contours = contours
    while len(current_contours) > 1:
        min_distance = None
        min_coordinate = None

        for x in range(len(current_contours)-1):
            for y in range(x+1, len(current_contours)):
                distance = calculate_contour_distance(current_contours[x], current_contours[y])
                if min_distance is None:
                    min_distance = distance
                    min_coordinate = (x, y)
                elif distance < min_distance:
                    min_distance = distance
                    min_coordinate = (x, y)

        if min_distance < threshold_distance:
            index1, index2 = min_coordinate
            current_contours[index1] = merge_contours(current_contours[index1], current_contours[index2])
            del current_contours[index2]
        else: 
            break

    return current_contours


def is_any_center_within_x_bounds(bounding_rectangles, target_rectangle):
    """
    Checks if any rectangle's center point falls within the x-bounds of a target rectangle.

    Args:
        bounding_rectangles: A NumPy array of bounding rectangles (x, y, w, h).
        target_rectangle: The target rectangle (x, y, w, h) to check against.

    Returns:
        A boolean array where True indicates the center of the rectangle is within the
        x-bounds of the target rectangle, and False otherwise.
    """

    # Extract target rectangle bounds
    target_x = target_rectangle[0]
    target_x_end = target_x + target_rectangle[2]

    # Calculate center points of all rectangles
    center_x = (bounding_rectangles[:, 0] + bounding_rectangles[:, 2]) / 2

    # Check if center points are within target x-bounds
    within_bounds = (center_x >= target_x) & (center_x <= target_x_end)

    return np.any(within_bounds)

"""splits them by their fraction bars. It does this by getting the countours of the cropped image and splitting on the widest bounding box if there are more than 2 contours. otherwise checks if it's an = signs or just adds the whole image. """
def split_fractions(cropped_and_resized):
    final_results = []
    for img in cropped_and_resized:
        #only used for image display this line can be removed
        border_size = 10
        img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        img_copy = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        fixed_contours = []
        for c in contours:
            x,y,w,h = cv2.boundingRect(c)
            if x < 8 or (x+w) > 68 or y < 8 or (y + h) > 68: continue
            fixed_contours.append(c)
        #fixed_contours = agglomerative_cluster(fixed_contours, threshold_distance=2.0)
        cv2.drawContours(img_copy, fixed_contours, -1, (0,0,255), 1)
        bounding_rectangles = np.array([cv2.boundingRect(c) for c in fixed_contours])
        if (len(bounding_rectangles) == 0):
            final_results.append([color_img, None, None, None, None])
        elif (len(bounding_rectangles) == 1):
            final_results.append([color_img, None, None, None, None])
        else: 
            bounding_rectangles = bounding_rectangles[np.argsort(bounding_rectangles[:, 2])[::-1]]
            max_tuple = bounding_rectangles[np.argmax(bounding_rectangles[:, 2])]

            x,y,w,h = max_tuple
            if y + h > 56:
                copy_top = color_img[0:y-5, 0:color_img.shape[1]]
                copy_bottom = color_img[y-5:color_img.shape[0], 0:color_img.shape[1]]
            else:
                copy_top = color_img[0:y+h-4, 0:color_img.shape[1]]
                copy_bottom = color_img[y+h:color_img.shape[0], 0:color_img.shape[1]]


            final_results.append([copy_top, None, None, copy_bottom, img_copy])
    return final_results

def resize_and_maintain_aspect_ratio(image, target_width=None, target_height=None): 

    # Get the original dimensions of the image
    original_height, original_width = image.shape[:2]

    # If both target_width and target_height are None, return the original image
    if target_width is None and target_height is None:
        return image

    # Calculate the aspect ratio of the original image
    aspect_ratio = original_width / original_height

    # Calculate the new dimensions
    if target_width is not None:
        # If target width is specified, calculate the target height
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # If target height is specified, calculate the target width
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return resized_image


def  is_minus_sign(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply GaussianBlur to reduce noise and improve contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply thresholding to get a binary image
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Loop over the contours
    if len(contours) > 1:
        return False
    for contour in contours:
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate the aspect ratio
        aspect_ratio = float(w) / h
        
        # Check if the aspect ratio indicates a horizontal line
        if aspect_ratio > 1.5:  # Adjust this threshold based on your specific use case
            # Optional: Draw the contour and bounding box for visualization
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            return True
    
    return False


def process_string(input_string):
    # Remove all periods
    result = input_string.replace(".", "")
    
    # Replace characters as specified
    #Currently I am replacing -- with = this may cause issues for negative detection in the future so be warned
    replacements = {
        ":": "=",
        "q": "9",
        "z": "2",
        "Z": "2",
        "*": "x",
        "|": "1",
        "l": "1",
        "(- / -)": "=",
        "?": "-",
        "I": "1",
        "!": "1",
        "G": "6",
        "i": "1",
        "J":"1",
        "j": "1",
        "L": "1",
        "o":"0",
        "--": "="
    }
    
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Remove any remaining alphabetic letters other than "x"
    result = re.sub(r'[a-wy-zA-WY-Z]', '', result)
    
    return result

"""Change rec_model_dir to wherever your PaddleOCR model is stored. Otherwise this just runs the recognizer on all of the iamges and returns a string with substitutions. If you find a consistent issue with replacement add it to process string."""

def get_results(final_results , rec_model_dir="/User/corne/anaconda3/envs/paddleocr/Lib/site-packages/PaddleOCR/pretrain_models/model_inference/Student/inference"):
    # Initialize PaddleOCR
    ocr = PaddleOCR(rec_model_dir=rec_model_dir,use_angle_cls=False, lang='en', drop_score=0.1)  # Specify the language ('en' for English)
    # Initialize result string
    result_string = ""
    result_bottom = None
    result_top = None
    # Iterate over final_results
    for final_test in final_results:
        copy_top = final_test[0]

        copy_bottom = final_test[3]

        # Perform OCR
        if copy_top is not None:
            result_top = ocr.ocr(copy_top, cls=True, det=False, rec=True)
        if copy_bottom is not None:
            print(copy_bottom)
            result_bottom = ocr.ocr(copy_bottom, cls=True, det=False, rec=True)

        # Extract text from OCR results
        top_text = result_top[0][0][0] if result_top and result_top[0] else ''
        bottom_text = result_bottom[0][0][0] if result_bottom and result_bottom[0] else ''
        if top_text != '' and bottom_text != '': division = ' / '
        else: division = ''

        if is_minus_sign(copy_top):
            top_text = "-"
        if copy_bottom is not None:
            if is_minus_sign(copy_bottom):
                bottom_text = "-"
        try:
            if "#" in bottom_text:
                result_string += "\n\n\n"
            if division == " / ":
                result_string += f"({top_text}{division}{bottom_text})"
            else:
                result_string += f"{top_text}{division}{bottom_text} "
        except Exception as e:
            print(e)
        result_top = None
        result_bottom = None
    return process_string(result_string)


def make_prediction(path):
    return get_results(split_fractions(crop_and_resize(bound_equations(segment_problems(path), segment_fractions(path)))))





class DocScanner(object):
    """An image scanner"""

    def __init__(self, interactive=False, MIN_QUAD_AREA_RATIO=0.25, MAX_QUAD_ANGLE_RANGE=40):
        """
        Args:
            interactive (boolean): If True, user can adjust screen contour before
                transformation occurs in interactive pyplot window.
            MIN_QUAD_AREA_RATIO (float): A contour will be rejected if its corners 
                do not form a quadrilateral that covers at least MIN_QUAD_AREA_RATIO 
                of the original image. Defaults to 0.25.
            MAX_QUAD_ANGLE_RANGE (int):  A contour will also be rejected if the range 
                of its interior angles exceeds MAX_QUAD_ANGLE_RANGE. Defaults to 40.
        """        
        self.interactive = interactive
        self.MIN_QUAD_AREA_RATIO = MIN_QUAD_AREA_RATIO
        self.MAX_QUAD_ANGLE_RANGE = MAX_QUAD_ANGLE_RANGE        

    def filter_corners(self, corners, min_dist=20):
        """Filters corners that are within min_dist of others"""
        def predicate(representatives, corner):
            return all(dist.euclidean(representative, corner) >= min_dist
                       for representative in representatives)

        filtered_corners = []
        for c in corners:
            if predicate(filtered_corners, c):
                filtered_corners.append(c)
        return filtered_corners

    def angle_between_vectors_degrees(self, u, v):
        """Returns the angle between two vectors in degrees"""
        return np.degrees(
            math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

    def get_angle(self, p1, p2, p3):
        """
        Returns the angle between the line segment from p2 to p1 
        and the line segment from p2 to p3 in degrees
        """
        a = np.radians(np.array(p1))
        b = np.radians(np.array(p2))
        c = np.radians(np.array(p3))

        avec = a - b
        cvec = c - b

        return self.angle_between_vectors_degrees(avec, cvec)

    def angle_range(self, quad):
        """
        Returns the range between max and min interior angles of quadrilateral.
        The input quadrilateral must be a numpy array with vertices ordered clockwise
        starting with the top left vertex.
        """
        tl, tr, br, bl = quad
        ura = self.get_angle(tl[0], tr[0], br[0])
        ula = self.get_angle(bl[0], tl[0], tr[0])
        lra = self.get_angle(tr[0], br[0], bl[0])
        lla = self.get_angle(br[0], bl[0], tl[0])

        angles = [ura, ula, lra, lla]
        return np.ptp(angles)          

    def get_corners(self, img):
        """
        Returns a list of corners ((x, y) tuples) found in the input image. With proper
        pre-processing and filtering, it should output at most 10 potential corners.
        This is a utility function used by get_contours. The input image is expected 
        to be rescaled and Canny filtered prior to be passed in.
        """
        lines = lsd(img)

        # massages the output from LSD
        # LSD operates on edges. One "line" has 2 edges, and so we need to combine the edges back into lines
        # 1. separate out the lines into horizontal and vertical lines.
        # 2. Draw the horizontal lines back onto a canvas, but slightly thicker and longer.
        # 3. Run connected-components on the new canvas
        # 4. Get the bounding box for each component, and the bounding box is final line.
        # 5. The ends of each line is a corner
        # 6. Repeat for vertical lines
        # 7. Draw all the final lines onto another canvas. Where the lines overlap are also corners

        corners = []
        if lines is not None:
            # separate out the horizontal and vertical lines, and draw them back onto separate canvases
            lines = lines.squeeze().astype(np.int32).tolist()
            horizontal_lines_canvas = np.zeros(img.shape, dtype=np.uint8)
            vertical_lines_canvas = np.zeros(img.shape, dtype=np.uint8)
            for line in lines:
                x1, y1, x2, y2, _ = line
                if abs(x2 - x1) > abs(y2 - y1):
                    (x1, y1), (x2, y2) = sorted(((x1, y1), (x2, y2)), key=lambda pt: pt[0])
                    cv2.line(horizontal_lines_canvas, (max(x1 - 5, 0), y1), (min(x2 + 5, img.shape[1] - 1), y2), 255, 2)
                else:
                    (x1, y1), (x2, y2) = sorted(((x1, y1), (x2, y2)), key=lambda pt: pt[1])
                    cv2.line(vertical_lines_canvas, (x1, max(y1 - 5, 0)), (x2, min(y2 + 5, img.shape[0] - 1)), 255, 2)

            lines = []

            # find the horizontal lines (connected-components -> bounding boxes -> final lines)
            (contours, hierarchy) = cv2.findContours(horizontal_lines_canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)[:2]
            horizontal_lines_canvas = np.zeros(img.shape, dtype=np.uint8)
            for contour in contours:
                contour = contour.reshape((contour.shape[0], contour.shape[2]))
                min_x = np.amin(contour[:, 0], axis=0) + 2
                max_x = np.amax(contour[:, 0], axis=0) - 2
                left_y = int(np.average(contour[contour[:, 0] == min_x][:, 1]))
                right_y = int(np.average(contour[contour[:, 0] == max_x][:, 1]))
                lines.append((min_x, left_y, max_x, right_y))
                cv2.line(horizontal_lines_canvas, (min_x, left_y), (max_x, right_y), 1, 1)
                corners.append((min_x, left_y))
                corners.append((max_x, right_y))

            # find the vertical lines (connected-components -> bounding boxes -> final lines)
            (contours, hierarchy) = cv2.findContours(vertical_lines_canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)[:2]
            vertical_lines_canvas = np.zeros(img.shape, dtype=np.uint8)
            for contour in contours:
                contour = contour.reshape((contour.shape[0], contour.shape[2]))
                min_y = np.amin(contour[:, 1], axis=0) + 2
                max_y = np.amax(contour[:, 1], axis=0) - 2
                top_x = int(np.average(contour[contour[:, 1] == min_y][:, 0]))
                bottom_x = int(np.average(contour[contour[:, 1] == max_y][:, 0]))
                lines.append((top_x, min_y, bottom_x, max_y))
                cv2.line(vertical_lines_canvas, (top_x, min_y), (bottom_x, max_y), 1, 1)
                corners.append((top_x, min_y))
                corners.append((bottom_x, max_y))

            # find the corners
            corners_y, corners_x = np.where(horizontal_lines_canvas + vertical_lines_canvas == 2)
            corners += zip(corners_x, corners_y)

        # remove corners in close proximity
        corners = self.filter_corners(corners)
        return corners

    def is_valid_contour(self, cnt, IM_WIDTH, IM_HEIGHT):
        """Returns True if the contour satisfies all requirements set at instantitation"""

        return (len(cnt) == 4 and cv2.contourArea(cnt) > IM_WIDTH * IM_HEIGHT * self.MIN_QUAD_AREA_RATIO 
            and self.angle_range(cnt) < self.MAX_QUAD_ANGLE_RANGE)


    def get_contour(self, rescaled_image):
        """
        Returns a numpy array of shape (4, 2) containing the vertices of the four corners
        of the document in the image. It considers the corners returned from get_corners()
        and uses heuristics to choose the four corners that most likely represent
        the corners of the document. If no corners were found, or the four corners represent
        a quadrilateral that is too small or convex, it returns the original four corners.
        """

        # these constants are carefully chosen
        MORPH = 9
        CANNY = 84
        HOUGH = 25

        IM_HEIGHT, IM_WIDTH, _ = rescaled_image.shape

        # convert the image to grayscale and blur it slightly
        gray = cv2.cvtColor(rescaled_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7,7), 0)

        # dilate helps to remove potential holes between edge segments
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(MORPH,MORPH))
        dilated = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

        # find edges and mark them in the output map using the Canny algorithm
        edged = cv2.Canny(dilated, 0, CANNY)
        test_corners = self.get_corners(edged)

        approx_contours = []

        if len(test_corners) >= 4:
            quads = []

            for quad in itertools.combinations(test_corners, 4):
                points = np.array(quad)
                points = transform.order_points(points)
                points = np.array([[p] for p in points], dtype = "int32")
                quads.append(points)

            # get top five quadrilaterals by area
            quads = sorted(quads, key=cv2.contourArea, reverse=True)[:5]
            # sort candidate quadrilaterals by their angle range, which helps remove outliers
            quads = sorted(quads, key=self.angle_range)

            approx = quads[0]
            if self.is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
                approx_contours.append(approx)

            # for debugging: uncomment the code below to draw the corners and countour found 
            # by get_corners() and overlay it on the image

            # cv2.drawContours(rescaled_image, [approx], -1, (20, 20, 255), 2)
            # plt.scatter(*zip(*test_corners))
            # plt.imshow(rescaled_image)
            # plt.show()

        # also attempt to find contours directly from the edged image, which occasionally 
        # produces better results
        (cnts, hierarchy) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

        # loop over the contours
        for c in cnts:
            # approximate the contour
            approx = cv2.approxPolyDP(c, 80, True)
            if self.is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
                approx_contours.append(approx)
                break

        # If we did not find any valid contours, just use the whole image
        if not approx_contours:
            TOP_RIGHT = (IM_WIDTH, 0)
            BOTTOM_RIGHT = (IM_WIDTH, IM_HEIGHT)
            BOTTOM_LEFT = (0, IM_HEIGHT)
            TOP_LEFT = (0, 0)
            screenCnt = np.array([[TOP_RIGHT], [BOTTOM_RIGHT], [BOTTOM_LEFT], [TOP_LEFT]])

        else:
            screenCnt = max(approx_contours, key=cv2.contourArea)
            
        return screenCnt.reshape(4, 2)

    def interactive_get_contour(self, screenCnt, rescaled_image):
        poly = Polygon(screenCnt, animated=True, fill=False, color="yellow", linewidth=5)
        fig, ax = plt.subplots()
        ax.add_patch(poly)
        ax.set_title(('Drag the corners of the box to the corners of the document. \n'
            'Close the window when finished.'))
        p = poly_i.PolygonInteractor(ax, poly)
        plt.imshow(rescaled_image)
        plt.show()

        new_points = p.get_poly_points()[:4]
        new_points = np.array([[p] for p in new_points], dtype = "int32")
        return new_points.reshape(4, 2)

    def scan(self, image_path):

        RESCALED_HEIGHT = 500.0
        OUTPUT_DIR = 'output'

        # load the image and compute the ratio of the old height
        # to the new height, clone it, and resize it
        image = cv2.imread(image_path)

        assert(image is not None)

        ratio = image.shape[0] / RESCALED_HEIGHT
        orig = image.copy()
        rescaled_image = imutils.resize(image, height = int(RESCALED_HEIGHT))

        # get the contour of the document
        screenCnt = self.get_contour(rescaled_image)

        if self.interactive:
            screenCnt = self.interactive_get_contour(screenCnt, rescaled_image)

        # apply the perspective transformation
        warped = transform.four_point_transform(orig, screenCnt * ratio)

        # save the transformed image

        cv2.imwrite(image_path, warped)

