from flask import Flask, request, jsonify
import os

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

SERVER_SUDO_PASSWORD = "qwerty"
USERS_DATA_SAVE_FOLDER_PATH = "users/"

@app.route("/hello_world")
def hello_world():

    client_ip = request.remote_addr

    print(f"{client_ip} request hello_world")
    return "Hello, World!"

@app.route("/")
def ok():
    return f"ok http://{host}:{port}"

if __name__ == "__main__":
    host = "172.19.150.39"
    port = 2222

    print(f"server started on http://{host}:{port}")
    app.run(host=host, port=port)
