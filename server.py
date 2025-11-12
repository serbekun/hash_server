from flask import Flask, request, send_from_directory, jsonify
import os
from XORFileCipher import encrypt_file, decrypt_file

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

SERVER_SUDO_PASSWORD = "qwerty"
USERS_DATA_SAVE_FOLDER_PATH = "users/"

SITES_FOLDER = "sites/"
MAIN_SITE = "main/"
HASHING_PHOTO_SITE = "hashing_photo/"

@app.route("/hello_world")
def hello_world():
    client_ip = request.remote_addr
    print(f"{client_ip} request hello_world")
    return "Hello, World!"

@app.route("/hashing_photo")
def hashing_photo():
    print(f"{request.remote_addr} request hashing_photo")
    return send_from_directory(SITES_FOLDER + HASHING_PHOTO_SITE, "index.html")

@app.route("/sites/hashing_photo/path:filename")
def hashing_photo_static(filename):
    return send_from_directory(SITES_FOLDER + HASHING_PHOTO_SITE, filename)

@app.route("/process_file", methods=["POST"])
def process_file():
    try:
        # check exist file in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        password = request.form.get('password')
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        mode = request.form.get('mode')  # 'encrypt' or 'decrypt'
        if mode not in ['encrypt', 'decrypt']:
            return jsonify({"error": "Invalid mode"}), 400
        
        # temp save uploaded file
        upload_folder = "uploads/"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        
        # process files 
        if mode == 'encrypt':
            output_path = encrypt_file(file_path, password)
        else:
            output_path = decrypt_file(file_path, password)
        
        # Return result
        return jsonify({
            "success": True,
            "message": "File processed successfully",
            "output_filename": os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)

@app.route("/")
def ok():
    print(f"{request.remote_addr} request /")

    html = ""
    with open(SITES_FOLDER + MAIN_SITE + "index.html", "r") as f:
        html = f.read()

    return f"{html}"
    from config import Config

from config import Config

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(SITES_FOLDER + HASHING_PHOTO_SITE, exist_ok=True)

    print(f"server started on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT)