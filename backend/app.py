from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image  # Import Image directly from PIL
from pdf2image import convert_from_path
import io  # For handling in-memory files
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import openai

load_dotenv()
app = Flask(__name__)

openai.api_key = os.getenv('OPEN_AI_API_KEY')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Correct CORS configuration (allow specific origin)
CORS(app, resources={r"/api/sendFiles": {"origins": "http://localhost:3000"}, r"/api/openAI": {"origins": "http://localhost:3000"}, r"/api/Gemini": {"origins": "http://localhost:3000"}})

@app.route('/api/sendFiles', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def upload_file():
    model = load_model('./mnist_digit_recognition_model.h5')
    result_string = ''
    files = request.files.getlist('file')  # Get multiple files

    # Create 'images' directory if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')

    for file in files:
        print("uploading File")
        filename = secure_filename(file.filename)
        file_path = os.path.join('images', filename)
        file.save(file_path)
        if file_path.find(".pdf") != -1:
            save_pdf_pages_as_png(file_path)

    for file in os.listdir('images'):
        if file.find('.pdf',0) != -1:
            continue
        else:
            description = getModelResponse('images/' + file, model)  # Pass the file path
            result_string += description

    # Delete all images in the 'images' directory after processing
    for file in os.listdir('images'):
        os.remove(os.path.join('images', file))

    return result_string  # Return the processed description



def getModelResponse(image_path, model):
    thresh_image = preprocess_image(image_path)
    digit_contours = find_digit_contours(thresh_image)
    predictions = classify_digits(model, thresh_image, digit_contours)
    output_string = ''
    for predicted_digit, (x, y, w, h) in predictions:
        output_string += str(predicted_digit)
    return output_string


def save_pdf_pages_as_png(pdf_path, output_dir="images"):
 # Convert the PDF file to PNG images
    pages = convert_from_path(pdf_path)

# Save the PNG images
    page_number = 0
    for page in pages:
        page.save(f"{output_dir}/page-{page_number}.png")
        print(f"{output_dir}/page-{page_number}.png")
        page_number += 1


def classify_digits(model, image, contours):
    digit_predictions = []
    for contour in contours:
        # Compute the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Crop and resize the image around the contour
        digit = image[y:y+h, x:x+w]
        digit = cv2.resize(digit, (28, 28))
        digit = np.expand_dims(digit, axis=-1)
        digit = np.expand_dims(digit, axis=0).astype('float32') / 255

        # prediction
        prediction = model.predict(digit)
        predicted_digit = np.argmax(prediction, axis=1)[0]  # Get the index of max predicted value
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
    prompt = request.form.get('string')
    response = openai.Completion.create(
    engine="gpt-3.5-turbo",  # You can use other engines like "gpt-3.5-turbo"
    prompt=prompt,
    max_tokens=1000,  # Adjust the number of tokens based on your needs
    n=1,  # Number of responses to generate
    stop=None,  # You can define stop sequences here if needed
    temperature=0.7  # Adjust the creativity of the output
    )
    return response.choices[0].text.strip()


@app.route('/api/Gemini', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def getGeminiResponse(file_path):
    """Analyzes a math image using Gemini Pro Vision and returns LaTeX expressions."""
    print("making Gemini Call")
    model = genai.GenerativeModel('gemini-pro-vision')
    with Image.open(file_path) as img:  # Open the image using Image.open
        # Convert image to bytes for Gemini Pro Vision
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        response = model.generate_content(
            ['If this image contains math problems Analyze it for each math problem and list each one in LaTeX', img],
            stream=True
        )
        print("done with gemini call")
        response.resolve()
        print(response.text)  # Print the Gemini response
        return response.text  # Return the content
if __name__ == '__main__':
    app.run(debug=True)



