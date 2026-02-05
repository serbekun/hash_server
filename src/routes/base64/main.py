from fastapi import APIRouter, Request
import base64

router = APIRouter()

from src.logging_utils import Logging

@router.post("/base64")
async def base64_ed(request: Request):
    """
    ## base64 server backend for get encoded and decoded string

    request json must contain 'text' and 'mod'
    
    Return:
        encode or decode text

    ### mods
    - 1 encode
    - 2 decode
    """
    Logging.server_log(f"{request.client.host} request base64_ed")
    
    try:
        data = await request.json()
    except:
        Logging.server_log("  Error: Invalid JSON")
        return {"error": "Invalid JSON"}, 400

    if not data or "text" not in data or "mod" not in data:
        Logging.server_log(f"  Error: text and mod is not requested")
        return {"error": "JSON must contain 'text' and 'mod'\n"}, 400

    text = data["text"]
    mod = data["mod"]

    processed_text = ""
    if mod == "1":
        bytes_data = text.encode('utf-8')
        encoded_bytes = base64.b64encode(bytes_data)
        processed_text = encoded_bytes.decode('ascii')
    elif mod == "2":
        try:
            decoded_bytes = base64.b64decode(text)
            processed_text = decoded_bytes.decode('utf-8')
        except Exception as e:
            Logging.server_log(f"  Error: encoding base64 was not successfully")
            return {"error": f"Error decoding base64: {str(e)}\n"}, 400
    else:
        Logging.server_log(f"  Error: Invalid mod {mod}")
        return {"error": "Invalid mod value"}, 400

    return {"result": processed_text}