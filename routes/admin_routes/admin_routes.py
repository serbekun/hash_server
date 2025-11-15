from flask import Blueprint, request
import os

from logging_utils import Logging
from config import Config
from Tokens import Tokens

bp = Blueprint("admin", __name__)

admin_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.ADMIN_TOKENS, token_length=15, token_start="admin_")

@bp.route("/", methods=["POST"])
def admin():
    Logging.server_log(f"{request.remote_addr} request /admin")

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
        Logging.server_log(" Incorrect token permission dined")
        return "Permission Denied"

@bp.route("/list_uploads", methods=["POST"])
def admin_list_uploads():
    Logging.server_log(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        Logging.server_log("  Error: token is not requested")
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission dined")
        return "Permission Denied"

    directory_path = Config.Paths.Client.UPLOADS

    files = ""

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            files += file_path + "\n"
    
    return files


@bp.route("/clear_uploads", methods=["POST"])
def admin_clear_upload():
    Logging.server_log(f"{request.remote_addr} request /admin/clear_uploads")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        Logging.server_log("  token is not requested")
        return "Error not label 'token' in json", 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission dined")
        return "Permission Denied"
    
    directory_path = Config.Paths.Client.UPLOADS

    if not os.path.isdir(directory_path):
        Logging.server_log(f"  Error: Directory '{directory_path}' does not exist.")
        return f"Error: Directory '{directory_path}' does not exist."

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                Logging.server_log("  Error: removing files was not ended")
                return "Error: removing files was not ended"
    Logging.server_log("  Successfully removed all files")
    return "Successfully removed all files"
    
@bp.route("/log", methods=["POST"])
def admin_log():
    Logging.server_log(f"{request.remote_addr} request /admin/log")

    data = request.get_json(force=True, silent=True)

    if not data or not "token" in data:
        Logging.server_log("  token is not requested")
        return "token is not requested"
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission dined")
        return "Permission Denied"

    log = ""
    with open(Config.Paths.Log.LOG_FOLDER + Config.Paths.Log.SERVER_LOG, "r") as f:
        log = f.read()
    
    return log