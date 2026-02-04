from fastapi import APIRouter, Request, UploadFile, File, Form
import os
from fastapi.responses import JSONResponse

router = APIRouter()

from src.logging_utils import Logging
from src.path_traversal_check import PathTraversal
from src.config import Config
from src.XORFileCipher import encrypt_file, decrypt_file
from src.Tokens import Tokens

download_tokens = Tokens(token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS, token_length=15, token_start="download_")

path_traversal = PathTraversal()

@router.post("/process_file")
async def process_file(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(...),
    mode: str = Form(...)
):
    Logging.server_log(f"{request.client.host} request process_file")

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        Logging.server_log(f"  Error: File too large {len(contents)}")
        return JSONResponse(
            {"error": f"File too large. Maximum size is {MAX_FILE_SIZE//1024//1024}MB"},
            status_code=413
        )

    try:
        if not file or file.filename == '':
            Logging.server_log("  Error: No selected file")
            return JSONResponse({"error": "No selected file"}, status_code=400)

        if not path_traversal.allowed_filename(file.filename):
            Logging.server_log(f"  Error: Invalid filename {file.filename}")
            return JSONResponse({"error": "Invalid filename"}, status_code=400)

        password = password.strip()
        if not password:
            Logging.server_log("  Error: Password is required")
            return JSONResponse({"error": "Password is required"}, status_code=400)

        if len(password) < 4:
            Logging.server_log("  Error: Password too short")
            return JSONResponse({"error": "Password must be at least 4 characters"}, status_code=400)

        if mode not in ['encrypt', 'decrypt']:
            Logging.server_log(f"  Error: Invalid mode {mode}")
            return JSONResponse({"error": "Invalid mode"}, status_code=400)

        upload_folder = Config.Paths.Client.UPLOADS
        os.makedirs(upload_folder, exist_ok=True)

        safe_file_path = path_traversal.safe_join(upload_folder, file.filename)
        if not safe_file_path:
            Logging.server_log(f"  Error: Path traversal detected for {file.filename}")
            return JSONResponse({"error": "Invalid file path"}, status_code=400)

        if os.path.exists(safe_file_path):
            Logging.server_log(f"  Error: File already exists {safe_file_path}")
            return JSONResponse({"error": "File already exists"}, status_code=409)

        # Save uploaded file
        with open(safe_file_path, 'wb') as f:
            f.write(contents)
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
            return JSONResponse({"error": "File processing failed"}, status_code=500)

        token = download_tokens.gen_token()
        download_tokens.add_token(token)

        if not Config.FileManaging.LEAVE_UPLOADED_FILE and os.path.exists(safe_file_path):
            try:
                os.remove(safe_file_path)
                Logging.server_log(f"  Removed temp file {os.path.basename(safe_file_path)}")
            except OSError as e:
                Logging.server_log(f"  Warning: Failed to remove temp file: {e}")

        return JSONResponse({
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
        return JSONResponse({"error": "Internal server error"}, status_code=500)
