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
    

    for file in os.listdir('images'):
        os.remove(os.path.join('images', file))

    return result_string


def save_pdf_pages_as_png(pdf_path, output_dir="images"):
    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages):
        page.save(f"{output_dir}/page-{page_number}.png")



@app.route('/api/Gemini', methods=['POST'])
@cross_origin(origins="http://localhost:3000")
def gemini_call():
    data = request.get_json()
    prompt = data.get('data')
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(
            [f"You are a world class mathematics teacher with a specialty in recognizing children's errors in math problems, You will analyze a problem similar to this #1 (2 1/3) + (7 1/5) Student Answer: ((7 * 5)/(3 * 5)) + ((1 * 3)/(5 * 3)) = (35/15) + (3/15) = (38/15) = (2 8/15) = (2 8/15) and give aa seperate answer for each problem that highlights the places where the child made a mistake: {prompt}"],
            stream=True
        )
    response.resolve()
    return jsonify({'response': response.text.strip()})

if __name__ == '__main__':
    app.run(debug=True)
