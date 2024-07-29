from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from PIL import Image
from pdf2image import convert_from_path
from functions import make_prediction
import shutil

app = Flask(__name__)



@app.route('/api/sendFiles', methods=['POST'])
def upload_file():
    result_string = ""
    files = request.files.getlist('file')
    print(files)

    # Create a unique folder name
    unique_folder = os.path.join('images', str(uuid.uuid4()))
    os.makedirs(unique_folder, exist_ok=True)

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(unique_folder, filename)
        file.save(file_path)
        if file_path.endswith(".pdf"):
            save_pdf_pages_as_png(file_path, output_folder=unique_folder)

    for i, file in enumerate(os.listdir(unique_folder)):
        result_string += f"Page {str(i+1)}: \n\n"
        result_string += make_prediction(os.path.join(unique_folder, file))
        result_string += "\n\n"
        print(result_string)

    # Clean up the unique folder after processing
    shutil.rmtree(unique_folder)

    return result_string


def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
