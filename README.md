# Hash Server 🔒

A secure file encryption and text encoding server with web interface and admin tools. Built with Flask (Python) and Rust client.

## Features ✨

- **File Encryption/Decryption** - XOR cipher with password protection
- **Base64 Encoding** - Text encoding/decoding via web interface
- **Secure File Upload** - Path traversal protection and file validation
- **Token-based Authentication** - Secure admin and download access
- **Web Interface** - User-friendly web UI for all operations
- **Admin Dashboard** - Server management and monitoring
- **Cross-platform Clients** - Python and Rust admin clients
- **Comprehensive Logging** - Detailed server activity logs

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- Rust (for admin client)
- Flask

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/serbekun/hash-server.git
cd hash-server
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure server settings**
```python
# Edit url_info.py
_IP = "your_server_ip"  # Use "127.0.0.1" for local development
_PORT = 2222
```

4. **Run the server**
```bash
python server.py
```

The server will start at `http://your_server_ip:2222`

## Usage 📖

### Web Interface
- **Main Page**: `http://your_server_ip:2222/`
- **File Encryption**: `http://your_server_ip:2222/hashing_file`
- **Base64 Tools**: `http://your_server_ip:2222/hashing_text_base64`

### File Encryption
1. Upload any file through the web interface
2. Set encryption password (minimum 4 characters)
3. Choose encrypt/decrypt mode
4. Download processed file using provided token

### Admin Access

#### Python Client
```bash
python admin_client.py
```
Available commands: `admin`, `clear_uploads`, `list_uploads`, `log`

#### Rust Client
```bash
cd admin_client
cargo run
```
Available commands: `admin`, `clear_uploads`, `list_uploads`, `log`, `set_token`

## API Documentation 🔧

### File Processing
```http
POST /hashing_file/process_file
Content-Type: multipart/form-data

file: [file]
password: [string]
mode: encrypt|decrypt
```

### Base64 Encoding
```http
POST /base64
Content-Type: application/json

{
  "text": "string",
  "mod": "1"  // 1=encode, 2=decode
}
```

### Admin Endpoints
All admin endpoints require valid token in JSON body:
```json
{"token": "admin_your_token_here"}
```

## Project Structure 🗂️

```
hash_server/
├── server.py                 # Main server
├── config.py                # Configuration
├── routes/                  # Flask blueprints
│   ├── admin_routes/
│   └── process_file/
├── templates/               # Web interfaces
│   ├── main/
│   ├── hashing_file/
│   └── hashing_text_base64/
├── admin_client/            # Rust admin client
│   └── src/
├── tokens/                  # Token storage
├── uploads/                 # Temporary file storage
└── log/                     # Server logs
```

## Security Features 🛡️

- **Path Traversal Protection** - Secure filename validation
- **Token Authentication** - Time-limited access tokens
- **File Size Limits** - 50MB maximum file size
- **Input Validation** - Comprehensive form validation
- **Secure File Handling** - Automatic temp file cleanup

## Configuration ⚙️

### Server Settings (`config.py`)
```python
class Config:
    class Link:
        HOST = "192.168.3.5"  # Server IP
        PORT = 2222           # Server port
    
    class FileManaging:
        LEAVE_UPLOADED_FILE = False  # Auto-cleanup
```

### Environment Variables
For production, use environment variables:
```bash
export SERVER_IP="your_ip"
export SERVER_PORT="2222"
```

## Development 🛠️

### Adding New Features
1. Create new blueprint in `routes/`
2. Add routes in `server.py`
3. Update admin client if needed

### Testing
```bash
# Test file encryption
python -c "from XORFileCipher import encrypt_file, decrypt_file; print('Cipher test passed')"

# Test server endpoints
python client.py
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing 🤝

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support 💬

For support and questions:
- Open an issue on GitHub
- Check the documentation in code comments

---

**Note**: This server is designed for secure internal networks. For production use, consider additional security measures like HTTPS, rate limiting, and firewall configuration.