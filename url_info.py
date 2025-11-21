import os
_IP = os.getenv('SERVER_IP', 'localhost')
_PORT = os.getenv('SERVER_PORT', '2222')

FULL_URL = f"http://{_IP}:{_PORT}"