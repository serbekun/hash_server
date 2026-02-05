import os
import re
import unicodedata

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

    def secure_filename(self, filename):
        """
        Secure a filename by removing dangerous characters.
        
        This is a replacement for werkzeug's secure_filename function.
        It performs the following operations:
        1. Normalizes unicode characters
        2. Removes path separators and other dangerous characters
        3. Removes leading/trailing dots and spaces
        4. Converts to ASCII, replacing non-ASCII characters with underscores
        5. Limits filename length
        
        Args:
            filename (str): The filename to secure
        
        Returns:
            str: A secured version of the filename, or an empty string if invalid
        
        Example:
            >>> validator = PathTraversal()
            >>> validator.secure_filename('../../../etc/passwd')
            'etc_passwd'
            >>> validator.secure_filename('My Document.pdf')
            'My_Document.pdf'
        """
        if not filename:
            return ""

        # Normalize unicode
        filename = unicodedata.normalize('NFKD', filename)
        
        # Convert to ASCII, ignoring non-ASCII characters
        filename = filename.encode('ASCII', 'ignore').decode('ASCII')
        
        # Remove path separators and other dangerous characters
        filename = re.sub(r'[\\/*?:"<>|]', '', filename)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Remove leading/trailing dots, underscores and spaces
        filename = filename.strip('._ ')
        
        # Limit filename length (255 is common max for most filesystems)
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        
        # If filename becomes empty after cleaning, return a default
        if not filename:
            filename = "file"
            
        return filename

    def safe_join(self, base_dir, filename):
        """
        Safely join a base directory with a filename, preventing path traversal attacks.
        
        This method:
        1. Sanitizes the filename using secure_filename method
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
        # Secure the filename using our own implementation
        filename = self.secure_filename(filename)
        if not filename:
            return None
        
        # Ensure base directory exists
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir, exist_ok=True)
            except (OSError, PermissionError):
                return None
        
        # Join paths and get absolute paths
        try:
            full_path = os.path.abspath(os.path.join(base_dir, filename))
            base_dir_abs = os.path.abspath(base_dir)
        except (TypeError, ValueError):
            return None

        # Check if the resulting path is within the base directory
        if not full_path.startswith(base_dir_abs):
            return None
        
        return full_path
