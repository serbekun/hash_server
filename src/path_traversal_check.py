import os
import re
from werkzeug.utils import secure_filename

class PathTraversal:
    """
    A security utility class for preventing path traversal attacks during file uploads.
    
    This class provides methods to validate filenames and safely construct file paths
    to prevent directory traversal attacks that could allow unauthorized access to
    files outside the intended directory.
    
    Attributes:
        allowed_extensions (set): Set of allowed file extensions for upload.
                                  Default includes common document, image, and archive formats.
    
    Example:
        >>> path_validator = PathTraversal()
        >>> safe_path = path_validator.safe_join('/uploads', 'user_file.pdf')
        >>> if safe_path:
        ...     # Safely save the file
        ...     with open(safe_path, 'wb') as f:
        ...         f.write(file_data)
    """
    
    def __init__(self):
        """
        Initialize the PathTraversal validator with default allowed file extensions.
        
        The default allowed extensions include:
        - Text files: txt
        - PDF documents: pdf
        - Images: jpg, jpeg, png
        - Office documents: doc, docx, xls, xlsx
        - Archives: zip, rar
        """
        self.allowed_extensions = {'txt', 'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

    def allowed_filename(self, filename):
        """
        Validate a filename for security and extension compliance.
        
        Performs three checks:
        1. Ensures filename is not empty and contains an extension
        2. Validates filename contains only safe characters (alphanumeric, underscore, hyphen, period)
        3. Checks if the file extension is in the allowed list
        
        Args:
            filename (str): The filename to validate
        
        Returns:
            bool: True if the filename passes all security checks and has an allowed extension,
                  False otherwise.
        
        Example:
            >>> validator = PathTraversal()
            >>> validator.allowed_filename('document.pdf')  # Returns: True
            >>> validator.allowed_filename('../../../etc/passwd')  # Returns: False
            >>> validator.allowed_filename('script.exe')  # Returns: False (extension not allowed)
        """
        if not filename or '.' not in filename:
            return False

        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False

        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        return file_ext in self.allowed_extensions

    def safe_join(self, base_dir, filename):
        """
        Safely join a base directory with a filename, preventing path traversal attacks.
        
        This method:
        1. Sanitizes the filename using werkzeug's secure_filename
        2. Converts both paths to absolute paths
        3. Ensures the resulting path is within the base directory
        4. Returns None if any security check fails
        
        Args:
            base_dir (str): The base directory where files should be stored
            filename (str): The filename to join with the base directory
        
        Returns:
            str or None: The absolute safe path if validation passes, None otherwise.
        
        Raises:
            Note: This method doesn't raise exceptions but returns None for invalid paths.
        
        Example:
            >>> validator = PathTraversal()
            >>> validator.safe_join('/var/www/uploads', '../../../etc/passwd')
            None
            >>> validator.safe_join('/var/www/uploads', 'myfile.pdf')
            '/var/www/uploads/myfile.pdf'
        """
        filename = secure_filename(filename)
        if not filename:
            return None
        
        full_path = os.path.abspath(os.path.join(base_dir, filename))
        base_dir = os.path.abspath(base_dir)

        if not full_path.startswith(base_dir):
            return None
        
        return full_path