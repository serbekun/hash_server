from flask import Flask, Response, request, send_from_directory
from datetime import datetime
import base64
import os

from config import Config
from Tokens import Tokens
from logging_utils import Logging

download_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS, token_length=15, token_start="download_")

app = Flask(__name__)


from routes.admin_routes.admin_routes import bp as admin_bp
from routes.process_file.process_file import bp as process_file_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(process_file_bp, url_prefix='/hashing_file')

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