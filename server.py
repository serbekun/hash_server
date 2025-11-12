from flask import Flask, request, send_from_directory, jsonify
import os

from XORFileCipher import encrypt_file, decrypt_file
from config import Config

app = Flask(__name__)

# cancel show don't needed logs 
import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.route("/hashing_file")
def hashing_photo():
    print(f"{request.remote_addr} request hashing_file")
    return send_from_directory(Config.Paths.SITES_FOLDER + Config.Paths.HASHING_FILE_SITE, "index.html")


@app.route("/sites/hashing_file/path:filename")
def hashing_photo_static(filename):
    return send_from_directory(Config.Paths.SITES_FOLDER + Config.Paths.HASHING_FILE_SITE, filename)


@app.route("/process_file", methods=["POST"])
def process_file():
    try:
        # check exist file in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        password = request.form.get('password')
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        mode = request.form.get('mode')  # 'encrypt' or 'decrypt'
        if mode not in ['encrypt', 'decrypt']:
            return jsonify({"error": "Invalid mode"}), 400
        
        # temp save uploaded file
        upload_folder = "uploads/"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        
        # process files 
        if mode == 'encrypt':
            output_path = encrypt_file(file_path, password)
        else:
            output_path = decrypt_file(file_path, password)
        
        # Return result
        return jsonify({
            "success": True,
            "message": "File processed successfully",
            "output_filename": os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)


@app.route("/")
def ok():
    print(f"{request.remote_addr} request /")

    html = ""
    with open(Config.Paths.SITES_FOLDER + Config.Paths.MAIN_SITE + "index.html", "r") as f:
        html = f.read()

    return f"{html}"


def main():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(Config.Paths.SITES_FOLDER + Config.Paths.HASHING_FILE_SITE, exist_ok=True)

    print(f"server started on http://{Config.Link.HOST}:{Config.Link.PORT}")
    app.run(host=Config.Link.HOST, port=Config.Link.PORT)


if __name__ == "__main__":
    main()