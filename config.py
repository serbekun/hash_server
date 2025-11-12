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
        HOST = "192.168.3.19"
        PORT = 2222

    class Paths:
        """
        Class contain
        - SITES_FOLDER
        - MAIN_SITE
        - HASHING_FILE_SITE
        """
        SITES_FOLDER = "sites/"
        MAIN_SITE = "main/"
        HASHING_FILE_SITE = "hashing_file/"
    
    class FileManaging:
        LEAVE_UPLOADED_FILE = True
