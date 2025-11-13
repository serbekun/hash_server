from flask import Flask, request, send_from_directory, jsonify
import base64
import os

from XORFileCipher import encrypt_file, decrypt_file
from config import Config
from Tokens import Tokens

admin_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.ADMIN_TOKENS, token_length=15, token_start="admin_")
download_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS, token_length=15, token_start="download_")

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
        
        token = download_tokens.gen_token()
        download_tokens.add_token(token)

        # Return result
        return jsonify({
            "success": True,
            "message": "File processed successfully",
            "output_filename": os.path.basename(output_path),
            "download_token": token
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/hashing_photo/<filename>", methods=["POST"])
def download_file(filename):

    print(f"{request.remote_addr} request download {filename}:")

    data = request.get_json(force=True, silent=True)

    if not data or "token" not in data:
        return "Error: labels don't contain 'token'", 400
    
    token = data["token"]
    if not download_tokens.check_token(token):
        print(" Incorrect token permission denied")
        return "Permission Denied"
    
    download_tokens.remove_token(token)

    print(f" Send {filename}")
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
        text = "" \
        "/admin/uploads"
        ""

        return text
    else:
        return "Permission Denied"

@app.route("/admin/list_uploads", methods=["POST"])
def admin_list_uploads():
    print(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        return "Permission Denied"

    directory_path = Config.Paths.Client.UPLOADS

    files = ""

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            files += file_path + "\n"
    
    return files


@app.route("/admin/clear_uploads", methods=["POST"])
def admin_clear_upload():
    print(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        return "Permission Denied"
    
    directory_path = Config.Paths.Client.UPLOADS

    if not os.path.isdir(directory_path):
        return f"Error: Directory '{directory_path}' does not exist."

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                return "Error: removing files was not ended"
    return "Successfully removed all files"
    

@app.route("/")
def ok():
    print(f"{request.remote_addr} request /")

    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.MAIN_SITE, "index.html")


def create_server_dirs():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("tokens", exist_ok=True)
    os.makedirs(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, exist_ok=True)


def main():

    create_server_dirs()

    print(f"server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    app.run(host=Config.Link.HOST, port=Config.Link.PORT)


if __name__ == "__main__":
    main()