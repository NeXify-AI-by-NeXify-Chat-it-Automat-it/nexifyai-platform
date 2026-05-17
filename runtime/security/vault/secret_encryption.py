#!/usr/bin/env python3
"""Secret Encryption — encrypts secrets at rest using Fernet."""
import base64, json, os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(salt=b'nexify-v1'):
    root = os.environ.get("DS_ADMIN_B01F400B__SECRET_KEY") or os.environ.get("DS_ADMIN_CF745C63__SECRET_KEY") or ""
    if not root: return None
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 600000)
    return base64.urlsafe_b64encode(kdf.derive(root.encode()))

def encrypt(v):
    k = derive_key()
    if not k: return v
    return Fernet(k).encrypt(v.encode()).decode()

def decrypt(t):
    k = derive_key()
    if not k: return t
    return Fernet(k).decrypt(t.encode()).decode()

if __name__ == "__main__":
    t = encrypt("test-value")
    d = decrypt(t) if t != "test-value" else "test-value"
    print(json.dumps({"has_key": derive_key() is not None, "enc_len": len(t), "decrypt_ok": d == "test-value"}))
