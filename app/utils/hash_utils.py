import json
import hashlib


def hash_payload(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(normalized).hexdigest()