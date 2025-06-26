import hashlib, hmac, os

def verify_signature(body: bytes, signature: str) -> bool:
    secret = os.getenv("LINE_CHANNEL_SECRET").encode()
    hash = hmac.new(secret, body, hashlib.sha256).digest()
    return hmac.compare_digest(hash, signature.encode())
