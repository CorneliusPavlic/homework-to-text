from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path
import io
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from openai import OpenAI

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})



client = OpenAI(
api_key=os.getenv('OPEN_AI_API_KEY')
) 
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

@app.route('/api/sendFiles', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def upload_file():
    # model = load_model('./mnist_digit_recognition_model.h5')
    result_string = ''
    files = request.files.getlist('file')

    if not os.path.exists('images'):
        os.makedirs('images')

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join('images', filename)
        file.save(file_path)
        if file_path.endswith(".pdf"):
            save_pdf_pages_as_png(file_path)

    for file in os.listdir('images'):
        if file.endswith('.pdf'):
            continue
        # if not gemini_call_for_math_detection('images/' + file):
        #     continue
        description = getGeminiResponse('images/' + file)
        result_string += description

    for file in os.listdir('images'):
        os.remove(os.path.join('images', file))

    return result_string

def getModelResponse(image_path, model):
    thresh_image = preprocess_image(image_path)
    digit_contours = find_digit_contours(thresh_image)
    predictions = classify_digits(model, thresh_image, digit_contours)
    output_string = ''
    for predicted_digit, (x, y, w, h) in predictions:
        output_string += str(predicted_digit)
    return output_string

def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")

def classify_digits(model, image, contours):
    digit_predictions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        digit = image[y:y+h, x:x+w]
        digit = cv2.resize(digit, (28, 28))
        digit = np.expand_dims(digit, axis=-1)
        digit = np.expand_dims(digit, axis=0).astype('float32') / 255
        prediction = model.predict(digit)
        predicted_digit = np.argmax(prediction, axis=1)[0]
        digit_predictions.append((predicted_digit, (x, y, w, h)))
    return digit_predictions

def find_digit_contours(preprocessed_image):
    contours, _ = cv2.findContours(preprocessed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
    return thresh

@app.route('/api/openAI', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def open_ai_call():
    data = request.get_json()
    prompt = data.get('data')
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo"
    )
    return jsonify({'response': response.choices[0].text.strip()})



@app.route('/api/Gemini', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def gemini_call():
    data = request.get_json()
    prompt = data.get('data')
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(
            [f"analze whether the follow math is correct : {prompt}"],
            stream=True
        )
    response.resolve()
    return jsonify({'response': response.text.strip()})


def gemini_call_for_math_detection(file_path):
    model = genai.GenerativeModel('gemini-pro-vision')
    with Image.open(file_path) as img:  # Open the image using Image.open
        # Convert image to bytes for Gemini Pro Vision
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
    response = model.generate_content(
            ["give me a binary response with 0 or 1, 0 if the page given does not contain any math formulas or 1 if it does contain math formulas.", img],
            stream=True
        )
    response.resolve()
    print(response.text)
    return("0" in response.text)




def getGeminiResponse(file_path):
    """Analyzes a math image using Gemini Pro Vision and returns LaTeX expressions."""
    print("making Gemini Call")
    model = genai.GenerativeModel('gemini-1.5-pro')
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        ]

    model = genai.GenerativeModel(model_name="gemini-1.5-pro",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)

    prompt_parts = [
        "input: ",
        "output: #1 (3/8) - (1/8) Student Answer: (3/8) - (1/8) = ((3 * 8)/(8 * 8)) -((8*8)/(8*8)) = (24/64) - (8/64) = (16/64) or (8/32) or (4/16) or (2/8) or (1/4)\n#2 (4/9) + (2/9)  Student Answer: (4/9) + (2/9) = ((4 * 9)/(9 * 9)) + ((2*9)/(9*9)) = (36/81) + (18/81) = (54/81) or (6/9) or (2/3) \n#3 (1/4) + (8/20) Student Answer: (1/4) + (8/20) = ((1 * 20)/(4 * 20)) + ((8*4)/(20*4)) = (20/80) + (32/80) = (52/80) or (26/40) or (13/20)\n#4 (4/6) - (2/10) Student Answer: (4/6) - (2/10) = ((4 * 10)/(6* 10)) - ((2*6)/(10*6)) = (40/60) - (12/60) = (28/60) or (14/30) or (7/15)\n#5 (1/2) - (1/11) Student Answer: (1/2) - (1/11) = ((1 * 11)/(2* 11)) - ((1*2)/(1*2)) = (11/22) - (2/22) = (9/22)\n#6 (1/2) + (1/4) Student Answer: (1/2) + (1/4) = ((1 * 4)/(2* 4)) + ((1*2)/(4*2)) = (4/8) + (2/8) = (6/8) or (3/4)\n#7 (3/5) + (1/15) Student Answer: (3/5) + (1/15) = ((3*15)/(5* 15)) + ((1*5)/(15*5)) = (45/75) + (5/75) = (50/75) or (2/3)\n#8 (4/6) - (4/8) Student Answer: (4/6) - (4/8) = ((4 * 8)/(6* 8)) - ((4*6)/(8*6)) = (32/48) - (24/48) = (8/48) or (4/24) or (2/12) or (1/6)\n#9 (2/4) - (2/7) Student Answer: (2/4) - (2/7) = ((2 * 7)/(4* 7)) - ((2*4)/(7*4)) = (14/28) - (8/28) = (6/28) or (3/14)\n#10 (6/7) + (2/21) Student Answer: (6/7) + (2/21) = ((6* 21)/(7*21)) + ((2*7)/(21*7)) = (126/147) + (14/147) = (140/147)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/0.jpg"),
        "output: #5 (1/2) - (1/11) Student Answer: ((1+2)/(11+2)) ((1+11)/(2+11)) (12/13) - (3/13) = (9/13)\n#6 (1/2) + (1/4) Student Answer: ((1+2)/(2+2)) = (3/4) + (1/4) = (4/4) = 1",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/1.jpg"),
        "output: #1 (3/8) - (1/8) Student Answer: = (2/8)\n#2 (4/9) + (2/9) Student Answer: = (6/9)\n#3 (1/4) + (8/20) Student Answer: = ((1+16)/(4+16)) = (17/20) + (8/20) = (25/20)\n#4 (4/6) - (2/10) Student Answer: = ((4+4)/(6+4)) = (8/10) - (2/10) = (6/10)\n#5 (1/2) - (1/11) Student Answer: = ((1+9)/(2+9)) = (10/11) - (1/11) = (9/11)\n#6 (1/2) + (1/4) Student Answer: = ((1+2)/(2+2)) = (3/4) + (1/4) = (4/4) or 1\n#7 (3/5) + (1/15) Student Answer: = ((3+10)/(5+10)) = (13/15) + (1/15) = (14/15)\n#8 (4/6) - (4/8) Student Answer: = ((4+2)/(6+2)) = (6/8) - (4/8) = (2/8)\n#9 (2/4) - (2/7) Student Answer: = ((2+3)/(4+3)) = (5/7) - (2/7) = (3/7)\n#10 (6/7) + (2/21) Student Answer: = ((6+14)/(7+14)) = (20/21) + (2/21) = (22/21)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/2.jpg"),
        "output: #1 (3/8) - (1/8) Student Answer: = (2/8) = (1/4)\n#2 (4/9) + (2/9) Student Answer (6/9) = (2/3)\n#3 (1/4) + (8/20) Student Answer: ((1+16)/(4+16)) = (17/20) + (8/20) = (25/20)\n#4 (4/6) - (2/10) Student Answer: ((4+10)/(6+10)) - ((2+6)/(6+10)) = (14/16) - (8/16) = (6/16)\n#5 (1/2) - (1/11) Student Answer: ((1+11)/(2+11)) - ((1+2)/(11+2)) = (12/13) - (3/13) = (9/13)\n#6 (1/2) + (1/4) Student Answer: ((1+2)/(2+2)) + (1/4) = (3/4) + (1/4) = (4/4) = 1\n#7 (3/5) + (1/15) Student Answer: ((3+10)/(5+10)) + (1/15) = (13/15) + (1/15) = (14/15)\n#8 (4/6) - (4/8) Student Answer: ((4+8)/(6+8)) - ((4+6)/(8+6)) = (12/14) - (10/14) = (2/14)\n#9 (2/4) - (2/7) Student Answer: ((2+7)/(4+7)) - ((2+4)/(7+4)) = (9/11) - (6/11) = (3/11)\n#10 (6/7) + (2/21) Student Answer: ((6+14)/(7+14)) + (2/21) = (20/21) + (2/21) = (22/21)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/3.jpg"),
        "output: #1 (3/8) - (1/8) Student Answer: = 2\n#2 (4/9) + (2/9) Student Answer: = (6/18)\n#3 (1/4) + (8/20) Student Answer: ((1+16)/(4+16)) + (8/20) = (17/20) + (8/20) = (25/20) = (5/4)\n#4 (4/6) - (2/10) Student Answer: ((4+4)/(6+4)) - (2/10) = (8/10) - (2/10) = (6/10) = (3/5)\n#5 (1/2) - (1/11) Student Answer: ((1+11)/(2+11)) - ((1+2)/11+2)) = (12/13) - (3/13) = (9/13)\n#6 (1/2) + (1/4) Student Answer: ((1+2)/(2+2)) + (1/4) = (3/4) + (1/4) = (4/4) = 1\n#7 (3/5) + (1/15) Student Answer: ((3+10)/(5+10)) + (1/15) = (13/15) + (1/15) = (14/15)\n#8 (4/6) - (4/8) Student Answer: ((4+8)/(6+8)) - ((4+6)/(8+6)) = (12/14) - (10/14) = (2/14) = (1/7)\n#9 (2/4) - (2/7) Student Answer: ((2+7)/(4+7) - ((2+4)/(7+4)) = (9/11) - (6/11) = (3/11)\n#10 (6/7) + (2/21) Student Answer: ((6+14)/(7+14) + (2/21) = (20/21) + (2/21) = (22/21)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/4.jpg"),
        "output: #1 (3/8) - (1/8) Student Answer: = (2/8)\n#2 (4/9) + (2/9) Student Answer: = (4/9)\n#3 (1/4) + (8/20) Student Answer: + (4/4) = (1/4) + (20/20) = (21/24) (21/24) + (12/24)= (33/24) = (11/8)\n#4 (4/6) - (2/10) Student Answer: (14/16) - (8/16) = (6/16) = (3/8)\n#5 (1/2) - (1/11) Student Answer: + (2/2) = (12/13) - (3/13) = (9/13)\n#6 (1/2) + (1/4) Student Answer: + (2/2) = (5/6) + (3/6) = (8/6) = (4/3)\n#7 (3/5) + (1/15) Student Answer: (18/20) + (6/20) = (24/20) = (6/5)\n#8 (4/6) - (4/8) Student Answer: (12/14) - (10/14) = (2/14) = (1/7)\n#9 (2/4) - (2/7)  Student Answer: (9/11) - (6/11) = (3/11)\n#10 (6/7) + (2/21) Student Answer: (27/28) + (9/28) = (26/28) = (13/14)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/5.jpg"),
        "output: #1 (2 1/3) + (7 1/5) Student Answer: ((1 * 5)/(3 * 5)) + ((1 * 3)/(5 * 3)) = (5/15) + (3/15) = (18/15) = (1 3/15) = (1 1/5)\n#2 (2 2/5) - (1 1/15) Student Answer: ((2 * 15)/(5 * 15)) - ((1 * 5)/(15 * 5)) = (30/75) - (5/75) = (25/75) = (1/5)\n#3 (6 5/6) - (4 5/12) Student Answer: ((5 * 12)/(6 * 12)) - ((5 * 6)/(12 * 6)) = (60/72) - (30/72) = (30/72) = (5/12)\n#4 (7 7/8) + (11 1/4) Student Answer: ((7 * 4)/(8 * 4)) + ((1 * 8)/(4 * 8)) = (28/32) + (8/32) = (36/32) = (1 4/32) =\n#5 (3 1/6) + (2 1/3) Student Answer: ((1 * 3)/(6 * 3)) + ((1 * 6)/(3 * 6)) = (3/18) + (6/18) = (9/18) = (1/2)\n#6 (12 3/4) - (6 7/14) Student Answer: ((3 * 14)/(4 * 14)) - ((7 * 4)/(14 * 4)) = (42/56) - (28/56) = (14/56) = (1/4)\n#7 (7 4/9) - (3 1/2) Student Answer: ((4 * 2)/(9 * 2)) - ((1 * 9)/(2 * 9)) = (8/18) - (9/18) = -(1/18)\n#8 (8 2/9) + (4 4/5) Student Answer: ((2 * 5)/(9 * 5)) + ((4 * 9)/(9 * 5)) = (46/90)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/6.jpg"),
        "output: #1 (2 1/3) + (7 1/5) Student Answer:  (7/3) + (36/5) = \n#2 (2 2/5) - (1 1/15) Student Answer: (12/5) - (16/15) = (36/15) - (16/15) = (20/15)\n#4 (6 5/6) - (4 5/12) Student Answer: (41/6) - (53/12) = (82/12) - (53/12) = (29/12)\n#5 (3 1/6) + (2 1/3) Student Answer: (19/6) + (7/3) = (19/6) + (14/6) = (33/6)\n#6 (12 3/4) - (6 7/14) Student Answer: (+10)(48/4) - (84/14) = (58/14) - (84/14) = (-34/14)\n#7 (7 4/9) - (3 1/2) Student Answer: (67/9) - (7/2) = (60/7)\n#8 (8 2/9) + (4 4/5) Student Answer: (41/9) + (20/4) = (131/13)",
        "input: ",
        genai.upload_file("./GeminiFullPageExamples/7.jpg"),
        "output: #1 (2 1/3) + (7 1/5) Student Answer: (17/3) + (36/5) = ((17 * 5)/(3 * 5)) - ((36 * 3)/(5 * 3)) = (35/15) + (108/15)  = (143/15) OR (9 8/15)\n#2 (2 2/5) - (1 1/15) Student Answer: (12/5) - (16/15) = ((12 * 15)/(5 * 15)) - ((16 * 5)/(15 * 5)) = (180/75) - (80/75) = (100/75) OR (1 1/3)\n#3 (6 5/6) - (4 5/12) Student Answer: (41/6) - (53/12) = ((41 * 12)/(6 * 12)) - ((53 * 6)/(12 * 6)) = (492/72) - (318/72) = (174/72) OR (2 30/72)\n#4 (7 7/8) + (11 1/4) Student Answer: (63/8) + (45/4) = ((63 * 4)/(8 * 4)) + ((45 * 8)/(4 * 8)) = (252/32) + (360/32) = (612/32) OR (19 1/8)\n#5 (3 1/6) + (2 1/3) Student Answer: (19/6) + (7/3) = (57/18) + (42/18) = (99/18) OR (5 1/2)\n#6 (12 3/4) - (6 7/14) Student Answer: (51/4) - (91/14) = (714/56) - (364/56) = (350/56)\n#7 (7 4/9) - (3 1/2) Student Answer: (67/9) - (7/2) = (134/18) - (63/18) = (71/18)\n#8 (8 2/9) + (4 4/5) Student Answer: (74/9) + (24/5) = (370/45) + (216/45) = (586/45)",
        "input: ",
        genai.upload_file(file_path),
        "output: ",
        ]

    response = model.generate_content(prompt_parts)
    return response.text


if __name__ == '__main__':
    app.run(debug=True)
