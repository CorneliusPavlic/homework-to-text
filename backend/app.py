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
    model = load_model('./mnist_digit_recognition_model.h5')
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
        description = getModelResponse('images/' + file, model)
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
            [f'analyze this as if you were a math teacher: {prompt}'],
            stream=True
        )
    response.resolve()
    return jsonify({'response': response.text.strip()})

if __name__ == '__main__':
    app.run(debug=True)
