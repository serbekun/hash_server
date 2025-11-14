from flask import Flask, request, send_from_directory, jsonify
from datetime import datetime
import base64
import os
import time

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

def server_log(log: str) -> None:
    """
    Print and save log to file
    """
    with open(Config.Paths.Log.LOG_FOLDER + Config.Paths.Log.SERVER_LOG, 'a') as f:
        try:
            f.write(f"{log}\n")
        except FileExistsError:
            print("Server Error: Error save log")
        
    print(log)

@app.route("/hashing_file")
def hashing_photo():
    server_log(f"{request.remote_addr} request hashing_file html")
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, "index.html")


@app.route("/hashing_text_base64")
def hashing_text_base64():
    server_log(f"{request.remote_addr} request hashing_text_base64 html")
    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_TEXT_BASE64, "index.html")


@app.route("/process_file", methods=["POST"])
def process_file():
    server_log(f"{request.remote_addr} request process_file")

    try:
        # check exist file in request
        if 'file' not in request.files:
            server_log("  Error: File is not requested")
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            server_log("  Error: No selected file in requested")
            return jsonify({"error": "No selected file"}), 400
        
        password = request.form.get('password')
        if not password:
            server_log("  Error: Password is not requested")
            return jsonify({"error": "Password is required"}), 400
        
        mode = request.form.get('mode')  # 'encrypt' or 'decrypt'
        if mode not in ['encrypt', 'decrypt']:
            server_log("  Error: Invalid mode")
            return jsonify({"error": "Invalid mode"}), 400
        
        # temp save uploaded file
        upload_folder = Config.Paths.Client.UPLOADS
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder) # TODO create function for create all dir and files
        
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        server_log(f"  Save temp file {file.filename}")

        # process files 
        if mode == 'encrypt':
            output_path = encrypt_file(file_path, password)
        else:
            output_path = decrypt_file(file_path, password)
        
        token = download_tokens.gen_token()
        download_tokens.add_token(token)

        if not Config.FileManaging.LEAVE_UPLOADED_FILE:
            try:
                os.remove(file_path)
            except OSError as e:
                server_log(f"Error: removing temp file {file_path} was not successfully")

        # Return result
        return jsonify({
            "success": True,
            "message": "File processed successfully",
            "output_filename": os.path.basename(output_path),
            "download_token": token
        })
        
    except Exception as e:
        server_log("  Internal server Error 500")
        return jsonify({"error": str(e)}), 500


from flask import Response

@app.route("/download/hashing_photo/<filename>", methods=["POST"])
def download_file(filename):

    server_log(f"{request.remote_addr}")

    path = os.path.join(Config.Paths.Client.UPLOADS, filename)

    data = request.get_json(force=True, silent=True)
    if not data or "token" not in data:
        server_log("  Error: token missing")
        return "Error: token missing", 400

    token = data["token"]
    if not download_tokens.check_token(token):
        server_log(" Permission denied")
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
            server_log(f"  Deleted {path}")
        except Exception as e:
            server_log(f"  Error deleting {path}: {e}")

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
    server_log(f"{request.remote_addr} request base64_ed")
    
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data or "mod" not in data:
        server_log(f"  Error: token and mod is not requested")
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
            server_log(f"  Error: encoding base64 was not successfully")
            return f"Error decoding base64: {str(e)}\n", 400

    return processed_text

@app.route("/admin", methods=["POST"])
def admin():
    server_log(f"{request.remote_addr} request /admin")

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
        server_log(" Incorrect token permission dined")
        return "Permission Denied"

@app.route("/admin/list_uploads", methods=["POST"])
def admin_list_uploads():
    server_log(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        server_log("  Error: token is not requested")
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        server_log(" Incorrect token permission dined")
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
    server_log(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        server_log("  token is not requested")
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        server_log(" Incorrect token permission dined")
        return "Permission Denied"
    
    directory_path = Config.Paths.Client.UPLOADS

    if not os.path.isdir(directory_path):
        server_log(f"  Error: Directory '{directory_path}' does not exist.")
        return f"Error: Directory '{directory_path}' does not exist."

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                server_log("  Error: removing files was not ended")
                return "Error: removing files was not ended"
    server_log("  Successfully removed all files")
    return "Successfully removed all files"
    
@app.route("/admin/log", methods=["POST"])
def admin_log():
    server_log(f"{request.remote_addr} request /admin/log")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        server_log("  token is not requested")
        return "token is not requested"
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        server_log(" Incorrect token permission dined")
        return "Permission Denied"

    log = ""
    with open(Config.Paths.Log.LOG_FOLDER + Config.Paths.Log.SERVER_LOG, "r") as f:
        log = f.read()
    
    return log

@app.route("/")
def ok():
    server_log(f"{request.remote_addr} request /")

    return send_from_directory(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.MAIN_SITE, "index.html")


def create_server_dirs():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("tokens", exist_ok=True)
    os.makedirs("log", exist_ok=True)
    os.makedirs(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, exist_ok=True)

def main():
    
    create_server_dirs()

    current_time_only = datetime.now().time()
    server_log(f"={current_time_only}=======================================================")
    server_log(f"server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    app.run(host=Config.Link.HOST, port=Config.Link.PORT)


if __name__ == "__main__":
    main()