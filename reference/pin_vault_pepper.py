"""Server-held pepper for PIN-vault key hardening.

The pepper is a secret that lives ONLY in the server environment / KMS — never
in the database. The PIN-vault key derivation folds it in via a blinded
round-trip (see ``POST /sync/encryption/pin-vault/harden``), so a database-only
compromise yields no offline brute-force oracle: an attacker cannot compute the
``hardened`` value without the pepper, and the pepper is in no DB table.

The keyring is versioned by ``kid``. **Never delete a kid** — a PIN vault stores
the kid it was created with and unlock must reproduce the same ``hardened``.
Only ever ADD kids when rotating. Keep ``kid`` strings <= 16 chars (the
``pepper_kid`` columns are ``VARCHAR(16)``).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from typing import Dict, Optional

from config import Config

logger = logging.getLogger(__name__)

_PEPPER_KEYRING_CACHE: Optional[Dict[str, bytes]] = None
_DEV_FALLBACK_KID = "pvdev1"


def _derive_pepper(material: str) -> bytes:
    return hashlib.sha256((material or "").encode("utf-8")).digest()


def pepper_keyring() -> Dict[str, bytes]:
    """Return ``{kid: 32-byte pepper}`` parsed from ``PIN_VAULT_PEPPER_KEYRING_JSON``.

    Falls back to a single DEV-ONLY kid (with a loud warning) when unset.
    """
    global _PEPPER_KEYRING_CACHE
    if _PEPPER_KEYRING_CACHE is not None:
        return _PEPPER_KEYRING_CACHE

    ring: Dict[str, bytes] = {}
    raw = (os.getenv("PIN_VAULT_PEPPER_KEYRING_JSON", "") or "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for kid, secret in parsed.items():
                    safe_kid = str(kid or "").strip()
                    safe_secret = str(secret or "").strip()
                    if safe_kid and safe_secret:
                        ring[safe_kid] = _derive_pepper(safe_secret)
        except Exception:
            ring = {}

    if not ring:
        # DEV-ONLY fallback. The pepper's entire value is being absent from the
        # database; a derived dev fallback is fine for local dev (the seed is an
        # env var, also not in the DB) but MUST be replaced with a real
        # PIN_VAULT_PEPPER_KEYRING_JSON before any production deployment, or the
        # PIN-vault hardening provides no protection.
        seed = (
            Config.AUTH_CRYPTO_KEY
            or Config.AUTH_JWT_SECRET
            or "dev-insecure-pin-vault-pepper"
        ).strip()
        ring = {_DEV_FALLBACK_KID: _derive_pepper("olace-pin-vault-pepper|" + seed)}
        logger.warning(
            "PIN_VAULT_PEPPER_KEYRING_JSON is not set — using an INSECURE dev "
            "fallback pepper (kid=%s). Set a real pepper keyring before any "
            "production deployment.",
            _DEV_FALLBACK_KID,
        )

    _PEPPER_KEYRING_CACHE = ring
    return ring


def active_pepper_kid() -> str:
    """The kid new vaults are created with. Honors ``PIN_VAULT_PEPPER_ACTIVE_KID``."""
    ring = pepper_keyring()
    configured = (os.getenv("PIN_VAULT_PEPPER_ACTIVE_KID", "") or "").strip()
    if configured and configured in ring:
        return configured
    return sorted(ring.keys())[-1]


def has_pepper_kid(kid: str) -> bool:
    return (kid or "").strip() in pepper_keyring()


def compute_hardened(blind: bytes, user_id: str, kid: str) -> bytes:
    """``HMAC-SHA256(pepper[kid], blind || utf8(user_id))``.

    ``blind`` is the client's ``HMAC(pinKey, "olace-pv-harden-blind-v1")``.
    Raises ``KeyError`` if ``kid`` is not in the keyring (never drop a kid).
    """
    ring = pepper_keyring()
    safe_kid = (kid or "").strip()
    if safe_kid not in ring:
        raise KeyError(f"Unknown PIN-vault pepper kid: {safe_kid!r}")
    msg = bytes(blind) + (user_id or "").encode("utf-8")
    return hmac.new(ring[safe_kid], msg, hashlib.sha256).digest()
