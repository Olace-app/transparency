"""Device identifier canonicalization helpers.

All persisted device IDs should use a deterministic pseudonymous form:
`didv1_<hmac_sha256>`.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from config import Config

_DEVICE_ID_PREFIX = "didv1_"


def _device_hash_key() -> bytes:
    seed = (Config.AUTH_CRYPTO_KEY or Config.AUTH_JWT_SECRET or os.getenv("API_KEY", "")).strip()
    if not seed:
        seed = "dev-insecure-device-hash-key"
    return seed.encode("utf-8")


def is_canonical_device_id(value: str) -> bool:
    raw = (value or "").strip().lower()
    if not raw.startswith(_DEVICE_ID_PREFIX):
        return False
    hex_part = raw[len(_DEVICE_ID_PREFIX):]
    return len(hex_part) == 64 and all(c in "0123456789abcdef" for c in hex_part)


def canonicalize_device_id(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if is_canonical_device_id(raw):
        return raw.lower()
    digest = hmac.new(_device_hash_key(), raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{_DEVICE_ID_PREFIX}{digest}"


def device_ids_match(left: str, right: str) -> bool:
    left_c = canonicalize_device_id(left)
    right_c = canonicalize_device_id(right)
    if not left_c or not right_c:
        return False
    return hmac.compare_digest(left_c, right_c)
