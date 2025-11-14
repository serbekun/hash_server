from flask import Flask, Response, request, send_from_directory, jsonify
from datetime import datetime
import base64
import os

from XORFileCipher import encrypt_file, decrypt_file
from config import Config
from Tokens import Tokens
from path_traversal_check import PathTraversal
from logging_utils import Logging

from admin_routes import bp as admin_bp


download_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS, token_length=15, token_start="download_")
path_traversal = PathTraversal()

app = Flask(__name__)

app.register_blueprint(admin_bp, url_prefix='/admin')

# cancel show don't needed logs 
import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.route("/hashing_file")
def hashing_photo():
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, "index.html")


@app.route("/templates/<path:path>")
def serve_templates_static(path):
    return send_from_directory("templates", path)


@app.route("/hashing_text_base64")
def hashing_text_base64():
    Logging.server_log(f"{request.remote_addr} request hashing_text_base64 html")
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_TEXT_BASE64, "index.html")


@app.route("/process_file", methods=["POST"])
def process_file():
    Logging.server_log(f"{request.remote_addr} request process_file")

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    if request.content_length and request.content_length > MAX_FILE_SIZE:
        Logging.server_log(f"  Error: File too large {request.content_length}")
        return jsonify({"error": f"File too large. Maximum size is {MAX_FILE_SIZE//1024//1024}MB"}), 413

    try:

        if 'file' not in request.files:
            Logging.server_log("  Error: No file provided")
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if not file or file.filename == '':
            Logging.server_log("  Error: No selected file")
            return jsonify({"error": "No selected file"}), 400

        if not path_traversal.allowed_filename(file.filename,):
            Logging.server_log(f"  Error: Invalid filename {file.filename}")
            return jsonify({"error": "Invalid filename"}), 400

        password = request.form.get('password', '').strip()
        if not password:
            Logging.server_log("  Error: Password is required")
            return jsonify({"error": "Password is required"}), 400

        if len(password) < 4:
            Logging.server_log("  Error: Password too short")
            return jsonify({"error": "Password must be at least 4 characters"}), 400

        mode = request.form.get('mode')
        if mode not in ['encrypt', 'decrypt']:
            Logging.server_log(f"  Error: Invalid mode {mode}")
            return jsonify({"error": "Invalid mode"}), 400

        upload_folder = Config.Paths.Client.UPLOADS
        os.makedirs(upload_folder, exist_ok=True)

        safe_file_path = path_traversal.safe_join(upload_folder, file.filename)
        if not safe_file_path:
            Logging.server_log(f"  Error: Path traversal detected for {file.filename}")
            return jsonify({"error": "Invalid file path"}), 400

        if os.path.exists(safe_file_path):
            Logging.server_log(f"  Error: File already exists {safe_file_path}")
            return jsonify({"error": "File already exists"}), 409

        file.save(safe_file_path)
        Logging.server_log(f"  Saved temp file {os.path.basename(safe_file_path)}")

        try:
            if mode == 'encrypt':
                output_path = encrypt_file(safe_file_path, password)
            else:
                output_path = decrypt_file(safe_file_path, password)
        except Exception as crypto_error:
            Logging.server_log(f"  Crypto error: {str(crypto_error)}")
            if os.path.exists(safe_file_path):
                os.remove(safe_file_path)
            return jsonify({"error": "File processing failed"}), 500

        token = download_tokens.gen_token()
        download_tokens.add_token(token)

        if not Config.FileManaging.LEAVE_UPLOADED_FILE and os.path.exists(safe_file_path):
            try:
                os.remove(safe_file_path)
                Logging.server_log(f"  Removed temp file {os.path.basename(safe_file_path)}")
            except OSError as e:
                Logging.server_log(f"  Warning: Failed to remove temp file: {e}")

        return jsonify({
            "success": True,
            "message": "File processed successfully",
            "output_filename": os.path.basename(output_path),
            "download_token": token
        })
        
    except Exception as e:
        Logging.server_log(f"  Internal server error: {str(e)}")
        if 'safe_file_path' in locals() and os.path.exists(safe_file_path):
            try:
                os.remove(safe_file_path)
            except:
                pass
        return jsonify({"error": "Internal server error"}), 500


@app.route("/download/hashing_photo/<filename>", methods=["POST"])
def download_file(filename):

    Logging.server_log(f"{request.remote_addr}")

    path = os.path.join(Config.Paths.Client.UPLOADS, filename)

    data = request.get_json(force=True, silent=True)
    if not data or "token" not in data:
        Logging.server_log("  Error: token missing")
        return "Error: token missing", 400

    token = data["token"]
    if not download_tokens.check_token(token):
        Logging.server_log(" Permission denied")
        return "Permission denied", 403

    download_tokens.remove_token(token)

    def generate():
        with open(path, "rb") as f:
            chunk = f.read(8192)
            while chunk:
                yield chunk
                chunk = f.read(8192)

        try:
            os.remove(path)
            Logging.server_log(f"  Deleted {path}")
        except Exception as e:
            Logging.server_log(f"  Error deleting {path}: {e}")

    return Response(
        generate(),
        mimetype="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


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
    Logging.server_log(f"{request.remote_addr} request base64_ed")
    
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data or "mod" not in data:
        Logging.server_log(f"  Error: token and mod is not requested")
        return "Error: JSON must contain 'text' and 'mod'\n", 400

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
            Logging.server_log(f"  Error: encoding base64 was not successfully")
            return f"Error decoding base64: {str(e)}\n", 400

    return processed_text

@app.route("/")
def ok():
    Logging.server_log(f"{request.remote_addr} request /")

    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.MAIN_SITE, "index.html")


def create_server_dirs():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("tokens", exist_ok=True)
    os.makedirs("log", exist_ok=True)
    os.makedirs(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, exist_ok=True)

def main():
    
    create_server_dirs()

    current_time_only = datetime.now().time()
    Logging.server_log(f"={current_time_only}=======================================================")
    Logging.server_log(f"server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    app.run(host=Config.Link.HOST, port=Config.Link.PORT)


if __name__ == "__main__":
    main()