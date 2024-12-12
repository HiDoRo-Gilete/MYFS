import string
import random
from math import floor
from getmac import get_mac_address
# python -m pip install pycryptodomex
from Cryptodome.Hash import SHA256
from Cryptodome.Cipher import AES 
from Cryptodome.Protocol.KDF import HKDF

def generateID(size=8, chars=string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def getMAC() -> str:
    return get_mac_address().replace(':', '')

def sha256(input: bytes) -> bytes:
    hash = SHA256.new()
    hash.update(input)
    return hash.digest()

def bytesToInt(input: bytes) -> int:
    return int.from_bytes(input, "big")

def strSize(n: int, unit: str = "bytes") -> str:
    divisor = 1
    if unit == "KB":
        divisor = 1024
    elif unit == "MB":
        divisor *= 1024
    elif unit == "GB":
        divisor *= 1024
    
    return str(floor(n/divisor)) + " " + unit

def hkdf(master_secret: str) -> bytes:
    salt = b'\x00' * 16
    key = HKDF(master_secret.encode(), 32, salt, SHA256)
    return key

def aesEncrypt(key: bytes, plain_text: bytes):
    cipher = AES.new(key, AES.MODE_CTR)
    cipher_text = cipher.encrypt(plain_text)
    nonce = cipher.nonce
    return cipher_text, nonce

def aesDecrypt(key: bytes, nonce: bytes, cipher_text: bytes):
    decrypt_cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    plain_text = decrypt_cipher.decrypt(cipher_text)
    return plain_text