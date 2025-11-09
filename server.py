from flask import Flask, request

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

SERVER_SUDO_PASSWORD = "qwerty"
USERS_DATA_SAVE_FOLDER_PATH = "users/"

# sites files
SITES_FOLDER = "sites/"
MAIN_SITE = "main/"

@app.route("/hello_world")
def hello_world():

    client_ip = request.remote_addr

    print(f"{client_ip} request hello_world")
    return "Hello, World!"

@app.route("/")
def ok():
    
    print(f"{request.remote_addr} request /")
    
    html = ""
    with open(SITES_FOLDER + MAIN_SITE + "index.html", "r") as f:
        html = f.read()
        
    return f"{html}"

if __name__ == "__main__":
    host = "192.168.3.19"
    port = 2222

    print(f"server started on http://{host}:{port}")
    app.run(host=host, port=port)
