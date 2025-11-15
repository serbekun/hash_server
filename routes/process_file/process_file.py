from flask import Blueprint, request, jsonify
import os

bp = Blueprint("process_file", __name__)

from logging_utils import Logging
from path_traversal_check import PathTraversal
from config import Config
from XORFileCipher import encrypt_file, decrypt_file
from Tokens import Tokens

download_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS, token_length=15, token_start="download_")

path_traversal = PathTraversal()

@bp.route("/process_file", methods=["POST"])
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