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
    try:
        return get_mac_address(interface="Ethernet").replace(':', '')
    except:
        pass
    return "000000000000"

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
    
    return str(floor(n/divisor)) + " " + ("" if unit == "bytes" else unit)

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
    try:
        decrypt_cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        plain_text = decrypt_cipher.decrypt(cipher_text)
        return plain_text
    except Exception as e: print(e)

def overwrite(fileobj, start,newbytes):
    fileobj.seek(start)
    fileobj.write(newbytes)    
    
def getFilename(path: str):
    parts = path.split('/')
    if len(parts) == 1:
        parts = path.split('\\')
    return parts[-1]

# ==============Print files===============

cols = ["Filename", "Size", "Creation date", "Modification date", "Import path", "Encryption"]
lens = [30, 15, 20, 20, 30, 10]     

def dStr(s, l):
    return [s[i*l:min((i+1)*l, len(s))] for i in range(0, len(s) // l + 1)]

def pStrs(attrArrs):
    maxLine = max([ len(arr) for arr in attrArrs])
    padd = "  "
    for li in range(0, maxLine):
        line = ""
        for ci, arr in enumerate(attrArrs):
            if li >= len(arr):
                line += lens[ci] * " " + padd
            else:
                line += arr[li] + (lens[ci] - len(arr[li])) * " " + padd
        print(line)

def printFiles(files):
    arrs = []
    arrs.append(dStr(cols[0],lens[0])) 
    arrs.append(dStr(cols[1],lens[1])) 
    arrs.append(dStr(cols[2],lens[2])) 
    arrs.append(dStr(cols[3],lens[3])) 
    arrs.append(dStr(cols[4],lens[4])) 
    arrs.append(dStr(cols[5],lens[5]))
    pStrs(arrs)
    if len(files) == 0:
        print("Empty")
        return
        
    for file in files:
        arrs = []
        arrs.append(dStr(str(file.get("filename")),lens[0])) 
        arrs.append(dStr(str(file.get("size")),lens[1])) 
        arrs.append(dStr(str(file.get("date create")),lens[2])) 
        arrs.append(dStr(str(file.get("date modifier")),lens[3])) 
        arrs.append(dStr(str(file.get("path")),lens[4])) 
        arrs.append(dStr(str(file.get("password")),lens[5])) 
        pStrs(arrs)
        