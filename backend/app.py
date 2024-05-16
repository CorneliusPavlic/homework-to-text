from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/api/sendFiles', methods=['POST'])
def upload_file():
    files = request.files
    for file in files:
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")

if __name__ == '__main__':
    app.run(debug=True)