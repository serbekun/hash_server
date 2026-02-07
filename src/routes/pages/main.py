from fastapi import APIRouter, Request 
import os
from fastapi.responses import FileResponse

router = APIRouter()

from src.logging_utils import Logging
from src.path_traversal_check import PathTraversal
from src.config import Config
from src.XORFileCipher import encrypt_file, decrypt_file
from src.Tokens import Tokens

@router.get("/hashing_file")
async def hashing_photo():
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.HASHING_FILE_SITE, "index.html")
    return FileResponse(file_path)


@router.get("/hashing_text_base64")
async def hashing_text_base64(request: Request):
    Logging.server_log(f"{request.client.host} request hashing_text_base64 html")
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.HASHING_TEXT_BASE64, "index.html")
    return FileResponse(file_path)

