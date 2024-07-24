import cv2
import numpy as np
import math
import re
from paddleocr import PaddleOCR

#returns the area of a box with the format top left corner, bottom right corner.
def box_area(box):
    return (box[1][0] - box[0][0]) * (box[1][1] - box[0][1])

def combine_two_closest_boxes(mergable_boxes):
    for i, box in enumerate(mergable_boxes):
        shortest_distance = (10000000, None)
        for j, destination in enumerate(mergable_boxes):
            if j != i:  # Avoid comparing the box with itself
                distance = distance_between_boxes(box, destination)
                if 0 < distance < 400 and distance < shortest_distance[0]:
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


def segment_problems(path):
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

    merge_margin_vertical = 70
    merge_margin_horizontal = 60
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
        new_box, i, j = combine_two_closest_boxes(mergable_boxes)
        if(new_box == None): flag = False
        else: 
            mergable_boxes.pop(i)
            mergable_boxes.pop(j-1)
            mergable_boxes.append(new_box)


    boxes = big_boxes + mergable_boxes


    bounded_problems = []
    for box in boxes:
        if (box[1][1] - box[0][1]) * (box[1][0] - box[0][0]) < 200: continue
        bounded_problems.append(([box[0][1], box[0][0]], [box[1][1], box[1][0]]))
    return bounded_problems


def segment_fractions(path):
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

    # go through the boxes and start merging
    merge_margin_vertical = 30
    merge_margin_horizontal = 1
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
        if area < 100 or (area < 400 and calculate_aspect_ratio(box) < 0.8): continue
        roi.append([copy[box[0][1]:box[1][1],box[0][0]:box[1][0]], [[box[0][1], box[0][0]], [box[1][1], box[1][0]]]])
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

def bound_equations(bounded_problems, roi):
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



def get_results(final_results):
    # Initialize PaddleOCR
    ocr = PaddleOCR(rec_model_dir="/User/corne/anaconda3/envs/paddleocr/Lib/site-packages/PaddleOCR/pretrain_models/model_inference/Student/inference",use_angle_cls=False, lang='en', drop_score=0.1)  # Specify the language ('en' for English)
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