import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import url_info

class Config:
    """
    Class for contain info about
    - class Links
    - class Paths
    - class FileManaging
    """

    class Link:
        """
        Class contain
        - HOST
        - PORT
        """
        HOST = url_info._IP
        PORT = url_info._PORT

    class Paths:
        """
        Class contain
        - class Sites
        - class Tokens
        """

        class Sites:
            SITES_FOLDER = "templates/"
            MAIN_SITE = "main/"
            HASHING_FILE_SITE = "hashing_file/"
            HASHING_TEXT_BASE64 = "hashing_text_base64/"

        class Tokens:
            TOKENS_FOLDER = "tokens/"
            ADMIN_TOKENS = "admin/tokens.txt"
            DOWNLOAD_TOKENS = "download/tokens.txt"

        class Client:
            UPLOADS = "uploads/"

        class Log:
            LOG_FOLDER = "log/"
            SERVER_LOG = "server.log"
    
    class ProcessFileConfig:
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    class FileManaging:
        LEAVE_UPLOADED_FILE = False
        SAVE_BASE64_TEXT = True
