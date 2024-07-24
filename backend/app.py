from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path
from functions import make_prediction

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})



genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

@app.route('/api/sendFiles', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def upload_file():
    result_string = ""
    files = request.files.getlist('file')
    print(files)
    if not os.path.exists('images'):
        os.makedirs('images')

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join('images', filename)
        file.save(file_path)
        if file_path.endswith(".pdf"):
            save_pdf_pages_as_png(file_path)

    for i, file in enumerate(os.listdir('images')):
        result_string += f"Page {str(i+1)}: \n\n"
        result_string += make_prediction(f"./images/{file}") 
        result_string += "\n\n"
        print(result_string)
    

    for file in os.listdir('images'):
        os.remove(os.path.join('images', file))

    return result_string


def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")

if __name__ == '__main__':
    app.run(debug=True)
