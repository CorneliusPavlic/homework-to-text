from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import uuid
import os
from PIL import Image
from pdf2image import convert_from_path
from functions import DocScanner
from functions import make_prediction

app = Flask(__name__)

@app.route('/api/sendFiles', methods=['POST'])
def upload_file():
    result_string = ""
    # Generate a unique directory name for this upload session
    unique_dir = os.path.join('uploads', str(uuid.uuid4()))
    os.makedirs(unique_dir, exist_ok=True)
    try:
        # Get the list of files from the request
        files = request.files.getlist('file')
        print("Received files:", files)
        scanner = DocScanner(False)
        
        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(unique_dir, filename)
            file.save(file_path)

            if file_path.endswith(".pdf"):
                save_pdf_pages_as_png(file_path)

        # Scan and make predictions on the saved files
        for file in os.listdir(unique_dir):
            file_path = os.path.join(unique_dir, file)
            scanner.scan(file_path)
            
        for i, file in enumerate(os.listdir(unique_dir)):
            file_path = os.path.join(unique_dir, file)
            prediction = make_prediction(file_path)
            if prediction == "":
                prediction = "No text found in this page"
            result_string += f"Page {str(i+1)}: \n\n  {[prediction]} \n\n"

        # Clean up by deleting the unique directory and its contents
        for file in os.listdir(unique_dir):
            os.remove(os.path.join(unique_dir, file))
        os.rmdir(unique_dir)

        return jsonify({"result": result_string}), 200
    except Exception as e:
        for file in os.listdir(unique_dir):
            os.remove(os.path.join(unique_dir, file))
            os.rmdir(unique_dir)
        return jsonify({"error": "Something went wrong with your file please try again"}), 500


def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")

if __name__ == '__main__':
    app.run(debug=True)

