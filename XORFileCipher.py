import os
from typing import Union, Optional

class XORFileCipher:
    """
    # Class for file encryption and decryption using XOR cipher
    
    ## Features:
    - Simple XOR encryption with password
    - Support for all file types
    - Automatic output filename generation
    
    ## Use example
    ```python
    if __name__ == "__main__":
        try:
            # Example use class
            cipher = XORFileCipher()
            
            # encrypt
            cipher.set_mode('encrypt')
            cipher.load_file('document.txt')
            encrypted_file = cipher.process('my_password')
            print(f"Encrypted: {encrypted_file}")
            
            # decrypt
            cipher.set_mode('decrypt')
            cipher.load_file(encrypted_file)
            decrypted_file = cipher.process('my_password')
            print(f"Decrypted: {decrypted_file}")
            
            # Example 2 use functions
            encrypted = encrypt_file('image.jpg', 'secret123')
            decrypted = decrypt_file(encrypted, 'secret123')
            
        except Exception as e:
            print(f"Error: {e}")
    ```    
    """
    
    def __init__(self):
        """
        # Initialize XORFileCipher object
        
        ## Example:
        ```python
        cipher = XORFileCipher()
        ```
        """
        self.mode = 'encrypt'
        self.selected_file = None


    def set_mode(self, mode: str):
        """
        # Set operation mode: encryption or decryption
        
        ## Arguments:
        - `mode` (str): Operation mode - 'encrypt' for encryption or 'decrypt' for decryption
        
        ## Example:
        ```python
        cipher.set_mode('encrypt')  # Set encryption mode
        cipher.set_mode('decrypt')  # Set decryption mode
        ```
        
        ## Exceptions:
        - ValueError: If invalid mode is provided
        """
        if mode not in ['encrypt', 'decrypt']:
            raise ValueError("Mode must be 'encrypt' or 'decrypt'")
        self.mode = mode
    

    def load_file(self, file_path: str):
        """
        # Load file for processing
        
        ## Arguments:
        - `file_path` (str): Path to the file to be processed
        
        ## Example:
        ```python
        cipher.load_file("document.txt")  # Load file for encryption/decryption
        ```
        
        ## Exceptions:
        - FileNotFoundError: If specified file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        self.selected_file = file_path


    def process(self, password: str, output_path: Optional[str] = None) -> str:
        """
        # Main file processing method - encrypt or decrypt based on current mode
        
        ## Arguments:
        - `password` (str): Password for XOR encryption/decryption
        - `output_path` (Optional[str]): Custom output file path (auto-generated if not provided)
        
        ## Returns:
        - `str`: Path to the processed output file
        
        ## Example:
        ```python
        # Encrypt file
        cipher.set_mode('encrypt')
        cipher.load_file("secret.txt")
        output_file = cipher.process("my_password")
        
        # Decrypt file
        cipher.set_mode('decrypt')
        cipher.load_file("secret.txt.encrypted")
        original_file = cipher.process("my_password")
        ```
        
        ## Exceptions:
        - ValueError: If no file is selected or password is empty
        """
        if not self.selected_file:
            raise ValueError("No file selected")
        
        if not password:
            raise ValueError("Password is required")
        
        # Read file data
        with open(self.selected_file, 'rb') as f:
            file_data = f.read()
        
        # Apply XOR cipher
        processed_data = self._xor_cipher(file_data, password)
        
        # Generate output filename if not provided
        if not output_path:
            output_path = self._generate_output_filename()
        
        # Write processed data to output file
        with open(output_path, 'wb') as f:
            f.write(processed_data)
        
        return output_path


    def _xor_cipher(self, data: bytes, password: str) -> bytes:
        """
        # Internal method - apply XOR cipher to data
        
        ## Arguments:
        - `data` (bytes): Input data to process
        - `password` (str): Password for XOR operation
        
        ## Returns:
        - `bytes`: Processed data after XOR operation
        """
        password_bytes = password.encode('utf-8')
        password_length = len(password_bytes)
        
        return bytes([
            data[i] ^ password_bytes[i % password_length] 
            for i in range(len(data))
        ])
    

    def _generate_output_filename(self) -> str:
        """
        # Internal method - generate output filename based on current mode
        
        ## Returns:
        - `str`: Generated output file path
        
        ## Example:
        - Input: "document.txt", mode: 'encrypt' → Output: "document.txt.encrypted"
        - Input: "document.txt.encrypted", mode: 'decrypt' → Output: "document_decrypted.txt"
        """
        base_name = self.selected_file
        
        if self.mode == 'encrypt':
            return f"{base_name}.encrypted"
        else:  # decrypt mode
            if base_name.endswith('.encrypted'):
                return base_name[:-10] + '_decrypted'
            else:
                return f"{base_name}_decrypted"
    
    
def encrypt_file(file_path: str, password: str, output_path: Optional[str] = None) -> str:
    """Encode file"""
    cipher = XORFileCipher()
    cipher.set_mode('encrypt')
    cipher.load_file(file_path)
    return cipher.process(password, output_path)


def decrypt_file(file_path: str, password: str, output_path: Optional[str] = None) -> str:
    """decode file"""
    cipher = XORFileCipher()
    cipher.set_mode('decrypt')
    cipher.load_file(file_path)
    return cipher.process(password, output_path)
