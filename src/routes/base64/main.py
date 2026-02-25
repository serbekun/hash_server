from fastapi import APIRouter, Request

router = APIRouter()

from src.logging_utils import Logging
from src.aes_crypto import encrypt_text_to_base64, generate_aes_key


@router.post("/encrypt_text")
async def aes_encrypt_text(request: Request):
    """
    Endpoint /v0/api/aes/encrypt_text

    Encrypt text with AES and return Base64 payload.
    """
    Logging.server_log(f"{request.client.host} request /v0/api/aes/encrypt_text")

    try:
        data = await request.json()
    except Exception:
        Logging.server_log("  Error: Invalid JSON")
        return {"error": "Invalid JSON"}, 400

    if not data or "text" not in data or "key" not in data:
        Logging.server_log("  Error: text or key is missing")
        return {"error": "JSON must contain 'text' and 'key'"}, 400

    text = str(data["text"])
    key = str(data["key"]).strip()

    if not key:
        Logging.server_log("  Error: AES key is empty")
        return {"error": "AES key is required"}, 400

    if len(key) < 4:
        Logging.server_log("  Error: AES key too short")
        return {"error": "AES key must be at least 4 characters"}, 400

    try:
        encrypted = encrypt_text_to_base64(text, key)
    except Exception as error:
        Logging.server_log(f"  Error: AES encryption failed: {error}")
        return {"error": "AES encryption failed"}, 500

    return {"result": encrypted}


@router.get("/generate_key")
async def aes_generate_key(request: Request):
    """
    Endpoint /v0/api/aes/generate_key

    Generate a random key for AES operations.
    """
    Logging.server_log(f"{request.client.host} request /v0/api/aes/generate_key")
    return {"key": generate_aes_key()}
