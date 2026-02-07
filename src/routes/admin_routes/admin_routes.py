from fastapi import APIRouter, Request
import os

from src.logging_utils import Logging
from src.config import Config
from src.Tokens import Tokens

router = APIRouter()

admin_tokens = Tokens(tokens_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.ADMIN_TOKENS, tokens_length=15, token_start="admin_")

@router.post("/")
async def admin(request: Request):
    Logging.server_log(f"{request.client.host} request /admin")

    data = await request.json()

    if not data or "token" not in data:
        return {"error": "Error not label 'token' in json"}, 400
    
    token = data["token"]

    if admin_tokens.check_token(token):
        text = "/admin/uploads"
        return text
    else:
        Logging.server_log(" Incorrect token permission denied")
        return "Permission Denied"

@router.post("/list_uploads")
async def admin_list_uploads(request: Request):
    Logging.server_log(f"{request.client.host} request /admin/list_uploads")

    try:
        data = await request.json()
    except:
        return {"error": "Invalid JSON"}, 400

    if not data or "token" not in data:
        Logging.server_log("  Error: token is not requested")
        return {"error": "Error not label 'token' in json"}, 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission denied")
        return "Permission Denied"

    directory_path = Config.Paths.Client.UPLOADS

    files = ""

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            files += file_path + "\n"
    
    return files


@router.post("/clear_uploads")
async def admin_clear_upload(request: Request):
    Logging.server_log(f"{request.client.host} request /admin/clear_uploads")

    try:
        data = await request.json()
    except:
        return {"error": "Invalid JSON"}, 400

    if not data or "token" not in data:
        Logging.server_log("  token is not requested")
        return {"error": "Error not label 'token' in json"}, 400
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission denied")
        return "Permission Denied"
    
    directory_path = Config.Paths.Client.UPLOADS

    if not os.path.isdir(directory_path):
        Logging.server_log(f"  Error: Directory '{directory_path}' does not exist.")
        return {"error": f"Error: Directory '{directory_path}' does not exist."}

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                Logging.server_log("  Error: removing files was not ended")
                return {"error": "Error: removing files was not ended"}
    Logging.server_log("  Successfully removed all files")
    return "Successfully removed all files"
    
@router.post("/log")
async def admin_log(request: Request):
    Logging.server_log(f"{request.client.host} request /admin/log")

    try:
        data = await request.json()
    except:
        return {"error": "Invalid JSON"}, 400

    if not data or "token" not in data:
        Logging.server_log("  token is not requested")
        return {"error": "token is not requested"}
    
    token = data["token"]

    if not admin_tokens.check_token(token):
        Logging.server_log(" Incorrect token permission denied")
        return "Permission Denied"

    log = ""
    with open(Config.Paths.Log.LOG_FOLDER + Config.Paths.Log.SERVER_LOG, "r") as f:
        log = f.read()
    
    return log
