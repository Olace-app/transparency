# Reference modules

Verbatim copies of two small server-side modules the white paper leans on. They are published as documentation: the backend imports its own copies, and these files are kept byte-identical to them by the backend's `check-transparency` target so the published text cannot lag what runs.

## pin_vault_pepper.py

The server half of the PIN vault derivation (white paper [section 3](../whitepaper/03-zero-knowledge-backups.md)). Applies a keyring-versioned pepper, provided by environment secret and never stored in the database, to the client's blinded value: `hardened = HMAC-SHA256(pepper[kid], blind || user_id)`. The module's own docstring documents the security model, including the loud dev-only fallback that production must not use.

## device_id.py

Identifier minimization at the front door. Raw OS device identifiers are canonicalized at ingress to `didv1_<HMAC-SHA256(server_key, raw_id)>`; only the HMAC form is stored or compared anywhere server-side, with constant-time comparison. The server never persists a raw hardware identifier.
