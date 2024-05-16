from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image  # Import Image directly from PIL
import io  # For handling in-memory files

app = Flask(__name__)

# Correct CORS configuration (allow specific origin)
CORS(app, resources={r"/api/sendFiles": {"origins": "http://localhost:3000"}})

@app.route('/api/sendFiles', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def upload_file():
    result_string = ''
    files = request.files.getlist('file')  # Get multiple files

    # Create 'images' directory if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join('images', filename)
        file.save(file_path)

        description = getGeminiResponse(file_path)  # Pass the file path
        result_string += description

    # Delete all images in the 'images' directory after processing
    for file in os.listdir('images'):
        os.remove(os.path.join('images', file))

    return result_string  # Return the processed description


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)  # Configure Google Generative AI


def getGeminiResponse(file_path):
    """Analyzes a math image using Gemini Pro Vision and returns LaTeX expressions."""
    model = genai.GenerativeModel('gemini-pro-vision')
    with Image.open(file_path) as img:  # Open the image using Image.open
        # Convert image to bytes for Gemini Pro Vision
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        response = model.generate_content(
            ['Analyze this image for each math problem and list each one in LaTeX', img],
            stream=True
        )
        response.resolve()
        print(response.text)  # Print the Gemini response
        return response.text  # Return the content


if __name__ == '__main__':
    app.run(debug=True)