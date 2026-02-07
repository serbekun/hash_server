from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os
import sys

# Add the project root to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.logging_utils import Logging

# adding other routers
from src.routes.admin_routes.admin_routes import router as admin_router
from src.routes.process_file.main import router as process_file_router
from src.routes.base64.main import router as base64_router
from src.routes.pages.main import router as pages_router

# Initialize FastAPI app
app = FastAPI(title="Hash Server")

# Include routers
app.include_router(admin_router, prefix="/v0/admin", tags=["admin"])
app.include_router(process_file_router, prefix="/v0/hashing_file", tags=["hashing"])
app.include_router(base64_router, prefix="/v0/api/base64", tags=["hashing"])
app.include_router(pages_router, prefix="/v0/pages", tags=["pages"])

# Mount static files for templates
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Web index of this site
@app.get("/")
async def ok(request: Request):
    Logging.server_log(f"{request.client.host} request /")
    file_path = os.path.join(Config.Paths.Sites.SITES_FOLDER, Config.Paths.Sites.MAIN_SITE, "index.html")
    return FileResponse(file_path)


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
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
