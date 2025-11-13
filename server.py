from flask import Flask, request, send_from_directory, jsonify
import base64
import os

from XORFileCipher import encrypt_file, decrypt_file
from config import Config
from Tokens import Tokens

admin_tokens = Tokens(Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.ADMIN_TOKENS, 15)
app = Flask(__name__)

# cancel show don't needed logs 
import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.route("/hashing_file")
def hashing_photo():
    print(f"{request.remote_addr} request hashing_file html")
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, "index.html")


@app.route("/hashing_text_base64")
def hashing_text_base64():
    print(f"{request.remote_addr} request hashing_text_base64 html")
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_TEXT_BASE64, "index.html")


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


@app.route("/download/hashing_photo/<filename>")
def download_file(filename):
    print(f"{request.remote_addr} request download {filename}")
    return send_from_directory("uploads", filename, as_attachment=True)


@app.route("/base64", methods=["POST"])
def base64_ed():
    """
    ## base64 server backend for get encoded and decoded string

    request json must contain 'text' and 'mod'
    
    Return:
        encode or decode text

    ### mods
    - 1 encode
    - 2 decode
    """
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data or "mod" not in data:
        return "Error: JSON must contain 'a' and 'b'\n", 400

    text = data["text"]
    mod = data["mod"]

    bytes = text.encode('utf-8')

    processed_text = ""
    if mod == "1":
        bytes = text.encode('utf-8')
        encoded_bytes = base64.b64encode(bytes)
        processed_text = encoded_bytes.decode('ascii')
    elif mod == "2":
        try:
            decoded_bytes = base64.b64decode(text)
            processed_text = decoded_bytes.decode('utf-8')
        except Exception as e:
            return f"Error decoding base64: {str(e)}\n", 400

    return processed_text

@app.route("/admin", methods=["POST"])
def admin():
    print(f"{request.remote_addr} request /admin")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if admin_tokens.check_token(token):
        return "its live good"
    else:
        return "Permission Denied"


@app.route("/")
def ok():
    print(f"{request.remote_addr} request /")

    html = ""
    with open(Config.Paths.SITES_FOLDER + Config.Paths.MAIN_SITE + "index.html", "r") as f:
        html = f.read()

    return f"{html}"


def create_server_dirs():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, exist_ok=True)


def main():

    create_server_dirs()

    print(f"server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    app.run(host=Config.Link.HOST, port=Config.Link.PORT)


if __name__ == "__main__":
    main()