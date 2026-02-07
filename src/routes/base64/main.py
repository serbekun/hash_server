from fastapi import APIRouter, Request
import base64

router = APIRouter()

from src.logging_utils import Logging

@router.post("/encode")
async def base64_encode(request: Request):
    """
    Endpoint /v0/api/base64/encode

    encode string to base64 format
    """
    Logging.server_log(f"{request.client.host} request /v0/api/base64/encode")
    
    # getting data from client
    try:
        data = await request.json()
    except:
        Logging.server_log("  Error: Invalid JSON")
        return {"error": "Invalid JSON"}, 400

    # validate data
    if not data or "text" not in data:
        Logging.server_log(f"  Error: text and is not requested")
        return {"error": "JSON must contain 'text'\n"}, 400

    # getting data from json
    text: str = data["text"]

    # encoding string to base64
    bytes_data = text.encode('utf-8')
    encoded_bytes = base64.b64encode(bytes_data)
    processed_text = encoded_bytes.decode('ascii')

    # send to client encoded string
    return {"result": processed_text}


@router.post("/decode")
async def base64_decode(request: Request):
    """
    Endpoint /v0/api/base64/decode

    decode base64 format to string
    """
    Logging.server_log(f"{request.client.host} request /v0/api/base64/decode")

    # getting data from client
    try:
        data = await request.json()
    except:
        Logging.server_log("  Error: Invalid JSON")
        return {"error": "Invalid JSON"}, 400

    # validate data
    if not data or "text" not in data or "mod" not in data:
        Logging.server_log(f"  Error: text is not requested")
        return {"error": "JSON must contain 'text'\n"}, 400

    # getting data from json
    text = data["text"]

    # decoding to string
    try:
        decoded_bytes = base64.b64decode(text)
        processed_text = decoded_bytes.decode('utf-8')
    except Exception as e:
        Logging.server_log(f"  Error: encoding base64 was not successfully")
        return {"error": f"Error decoding base64: {str(e)}\n"}, 400
    
    # send decoded base64 to client
    return {"result": processed_text}
