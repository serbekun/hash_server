import os
import re
from werkzeug.utils import secure_filename

class PathTraversal:

    def __init__(self):
        self.allowed_extensions = {'txt', 'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

    def allowed_filename(self, filename):
        if not filename or '.' not in filename:
            return False

        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False

        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        return file_ext in self.allowed_extensions

    def safe_join(self, base_dir, filename):

        filename = secure_filename(filename)
        if not filename:
            return None
        
        full_path = os.path.abspath(os.path.join(base_dir, filename))
        base_dir = os.path.abspath(base_dir)

        if not full_path.startswith(base_dir):
            return None
        
        return full_path
