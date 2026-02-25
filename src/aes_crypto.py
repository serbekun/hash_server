import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


AES_HEADER = b"AES1"
NONCE_SIZE = 12


def _derive_key(key_material: str) -> bytes:
    if not key_material:
        raise ValueError("Key is required")
    return hashlib.sha256(key_material.encode("utf-8")).digest()


def generate_aes_key() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")


def encrypt_bytes(data: bytes, key_material: str) -> bytes:
    key = _derive_key(key_material)
    nonce = os.urandom(NONCE_SIZE)
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, data, None)
    return AES_HEADER + nonce + ciphertext


def decrypt_bytes(data: bytes, key_material: str) -> bytes:
    if len(data) < len(AES_HEADER) + NONCE_SIZE + 1:
        raise ValueError("Invalid encrypted data")
    if not data.startswith(AES_HEADER):
        raise ValueError("Invalid AES header")

    key = _derive_key(key_material)
    nonce_start = len(AES_HEADER)
    nonce_end = nonce_start + NONCE_SIZE
    nonce = data[nonce_start:nonce_end]
    ciphertext = data[nonce_end:]
    cipher = AESGCM(key)
    return cipher.decrypt(nonce, ciphertext, None)


def encrypt_text_to_base64(text: str, key_material: str) -> str:
    encrypted = encrypt_bytes(text.encode("utf-8"), key_material)
    return base64.b64encode(encrypted).decode("ascii")


def encrypt_file(file_path: str, key_material: str, output_path: str | None = None) -> str:
    with open(file_path, "rb") as source_file:
        file_data = source_file.read()

    encrypted_data = encrypt_bytes(file_data, key_material)

    if output_path is None:
        output_path = f"{file_path}.aes"

    with open(output_path, "wb") as output_file:
        output_file.write(encrypted_data)

    return output_path


def decrypt_file(file_path: str, key_material: str, output_path: str | None = None) -> str:
    with open(file_path, "rb") as source_file:
        file_data = source_file.read()

    decrypted_data = decrypt_bytes(file_data, key_material)

    if output_path is None:
        if file_path.endswith(".aes"):
            output_path = file_path[:-4]
        else:
            output_path = f"{file_path}_decrypted"

    with open(output_path, "wb") as output_file:
        output_file.write(decrypted_data)

    return output_path
