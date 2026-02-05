from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os
import sys

# Add the project root to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.Tokens import Tokens
from src.logging_utils import Logging

# adding other routers
from src.routes.admin_routes.admin_routes import router as admin_router
from src.routes.process_file.process_file import router as process_file_router
from src.routes.base64.main import router as base64_router

# Initialize FastAPI app
app = FastAPI(title="Hash Server")

# Initialize download tokens
download_tokens = Tokens(
    token_file=Config.Paths.Tokens.TOKENS_FOLDER + Config.Paths.Tokens.DOWNLOAD_TOKENS,
    token_length=15,
    token_start="download_"
)

# Web index of this site
@app.get("/")
async def ok(request: Request):
    Logging.server_log(f"{request.client.host} request /")
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.MAIN_SITE, "index.html")
    return FileResponse(file_path)

# Include routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(process_file_router, prefix="/hashing_file", tags=["hashing"])
app.include_router(base64_router, prefix="", tags=["hashing"])

# Mount static files
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/hashing_file")
async def hashing_photo():
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.HASHING_FILE_SITE, "index.html")
    return FileResponse(file_path)


@app.get("/hashing_text_base64")
async def hashing_text_base64(request: Request):
    Logging.server_log(f"{request.client.host} request hashing_text_base64 html")
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.HASHING_TEXT_BASE64, "index.html")
    return FileResponse(file_path)


@app.post("/download/hashing_photo/{filename}")
async def download_file(filename: str, request: Request):
    Logging.server_log(f"{request.client.host} download request for {filename}")

    path = os.path.join(Config.Paths.Client.UPLOADS, filename)

    try:
        data = await request.json()
    except:
        Logging.server_log("  Error: Invalid JSON")
        return {"error": "Invalid JSON"}, 400

    if not data or "token" not in data:
        Logging.server_log("  Error: token missing")
        return {"error": "Error: token missing"}, 400

    token = data["token"]
    if not download_tokens.check_token(token):
        Logging.server_log(" Permission denied")
        return {"error": "Permission denied"}, 403

    download_tokens.remove_token(token)

    try:
        response = FileResponse(
            path,
            media_type="application/octet-stream",
            filename=filename
        )
        
        # Delete file after download
        def cleanup():
            try:
                os.remove(path)
                Logging.server_log(f"  Deleted {path}")
            except Exception as e:
                Logging.server_log(f"  Error deleting {path}: {e}")

        # Note: In FastAPI, file deletion needs to be handled differently
        # This is a background task that can be implemented with BackgroundTasks
        return response
    except FileNotFoundError:
        Logging.server_log(f"  File not found: {path}")
        return {"error": "File not found"}, 404


def create_server_dirs():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("tokens", exist_ok=True)
    os.makedirs("log", exist_ok=True)
    os.makedirs(Config.Paths.Sites.SITES_FOLDER + Config.Paths.Sites.HASHING_FILE_SITE, exist_ok=True)


def main():
    import uvicorn
    
    create_server_dirs()

    current_time_only = datetime.now().time()
    Logging.server_log(f"={current_time_only}=======================================================")
    Logging.server_log(f"FastAPI server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    
    uvicorn.run(
        "src.server:app",
        host=Config.Link.HOST,
        port=Config.Link.PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
