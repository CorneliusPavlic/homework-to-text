from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path
from functions import DocScanner
from functions import make_prediction

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})



@app.route('/api/sendFiles', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def upload_file():
    result_string = ""
    return jsonify({"result": "I'm so freaking done rn"}), 200
    #     # Check if the 'images' directory exists, if not, create it
    # if not os.path.exists('images'):
    #     os.makedirs('images')

    #     # Get the list of files from the request
    # files = request.files.getlist('file')
    # print("Received files:", files)
    # scanner = DocScanner(False)
    # if not files:
    #     return jsonify({"error": "No files uploaded"}), 400

    #     # Save each file to the 'images' directory
    # print(f"We have {files}, Files is {len(files)} long")
    # for file in files:
    #     filename = secure_filename(file.filename)
    #     file_path = os.path.join('images', filename)
    #     print(f"Saving file to {file_path}")
    #     file.save(file_path)

    #         # If the file is a PDF, convert it to images (assuming this function is implemented)
    #     if file_path.endswith(".pdf"):
    #         save_pdf_pages_as_png(file_path)  # Convert PDF pages to PNG
    # for file in os.listdir('images'):
    #     file_path = os.path.join('images', filename)
    #     print(file_path)
    #     scanner.scan(file_path)
    #     # Make predictions on the saved files
    # for i, file in enumerate(os.listdir('images')):
    #     file_path = os.path.join('images', file)
    #     print(f"Processing file {file_path}")
    #     result_string += f"Page {str(i+1)}: \n\n"
    #     result_string += make_prediction(file_path)  # Assuming this function returns a string
    #     result_string += "\n\n"

    # # Clean up the 'images' directory
    # for file in os.listdir('images'):
    #     os.remove(os.path.join('images', file))
    # print("Cleaned up the 'images' directory.")

    # return jsonify({"result": result_string}), 200



def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")

if __name__ == '__main__':
    app.run(debug=True)
