from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image  # Import Image directly from PIL
from pdf2image import convert_from_path
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
            description = getGeminiResponse('images/' + file)  # Pass the file path
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



def save_pdf_pages_as_png(pdf_path, output_dir="images"):
 # Convert the PDF file to PNG images
    pages = convert_from_path(pdf_path)

# Save the PNG images
    page_number = 0
    for page in pages:
        page.save(f"{output_dir}/page-{page_number}.png")
        print(f"{output_dir}/page-{page_number}.png")
        page_number += 1



if __name__ == '__main__':
    app.run(debug=True)