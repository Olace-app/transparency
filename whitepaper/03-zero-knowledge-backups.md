# 3. Zero-knowledge cloud backups

Cloud backup is optional. When enabled, everything is encrypted on your device before upload; the server stores envelopes it cannot open. The code below lives in [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart) and ships verbatim in the app. Formats are pinned by [test-vectors/zk_vectors.json](../test-vectors/zk_vectors.json).

## Key hierarchy

```
Recovery Key (16 bytes, shown once, Crockford Base32)
   │  HKDF-SHA256, salt "olace-zk-recovery-v1", info "mk-wrap|<userId>"
   ▼
wrapping key ──AES-256-GCM──► wrapped_mk  (the only MK form the server sees)

Master Key (MK, 32 random bytes, never leaves your devices)
   │  HKDF-SHA256, salt "olace-zk-data-v1", info = purpose string
   ▼
per-object data keys ──AES-256-GCM──► zk1 envelopes
```

- **Master Key**: generated on your device (`ZkCrypto.generateKeys`, [src/zk_crypto.dart](https://github.com/Olace-app/olace-crypto-dart/blob/main/lib/src/zk_crypto.dart)). Stored in the OS keystore on desktop and mobile; memory-only per session on web.
- **Recovery Key**: 16 random bytes formatted as `XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-X` ([src/recovery_key.dart](https://github.com/Olace-app/olace-crypto-dart/blob/main/lib/src/recovery_key.dart)). It wraps the MK; the server stores only the wrapped result. Without the Recovery Key and every other unlock method, backups cannot be recovered, by Olace or by anyone else. This is by design; see [08](08-known-limitations.md).
- **Per-purpose data keys**: every object class and id gets its own key via the purpose string (`conv|<userId>|<conversationId>`, `proj|...`, `rctx|...`, `instr|...`, `byok_vault|...`, `media|<userId>|<attachmentId>`). No two objects share an AES key, and the purpose doubles as GCM AAD, so a ciphertext cannot be replayed in another context.

## The zk1 envelope

`"zk1:" + base64url( nonce(12) || ciphertext || tag(16) )`, AES-256-GCM. Media blobs use the same layout as raw bytes without the prefix. Attachment file names and MIME types are encrypted with the attachment's data key with the field name bound into the AAD (`media-meta|<userId>|<attachmentId>|<field>`).

Server-side, `zk1` is the only accepted and the only representable mode: the sync API rejects plaintext checkpoints, the write layer raises on any non-zk1 record, and the database carries `CHECK (enc_mode = 'zk1')` on all three backup tables (migration `0057_zero_knowledge_only`).

## The PIN vault

A PIN is convenient but low-entropy (a 4 to 6 digit PIN has about 13 to 20 bits). The vault makes a database dump useless for offline PIN cracking by splitting the derivation between your device and a server-held secret ([src/pin_vault.dart](https://github.com/Olace-app/olace-crypto-dart/blob/main/lib/src/pin_vault.dart), server side annotated in [reference/pin_vault_pepper.py](../reference/pin_vault_pepper.py)):

1. **Device**: `pin_key = Argon2id(PIN, salt)` (new vaults: t=2, m=32 MiB, p=4; existing vaults keep their stored params).
2. **Device**: `blind = HMAC-SHA256(pin_key, "olace-pv-harden-blind-v1")`. Only this one-way value is sent to the server. The server never sees the PIN or the PIN key.
3. **Server**: `hardened = HMAC-SHA256(pepper[kid], blind || userId)`. The pepper lives in a versioned keyring provided by environment secret (`PIN_VAULT_PEPPER_KEYRING_JSON`), never in the database. The endpoint is read-only and rate limited per minute, hour and day; wrong attempts decrement a counter that locks the vault.
4. **Device**: `vault_key = HKDF-SHA256(pin_key, salt=hardened, info="olace-pin-vault-key-v2")`. The vault key decrypts the Recovery Key envelope; an auth tag derived from the vault key is stored server-side only as its SHA-256 hash.

Result: cracking the vault offline requires the database AND the pepper AND an Argon2id search per guess. An attacker with only the database cannot test a single guess.

## Web sessions

On web, the MK lives only in browser memory for the session. "Trust this browser" persists a wrapped MK under a non-extractable WebCrypto key in IndexedDB; the raw MK is never written to browser storage of any kind. See [08](08-known-limitations.md) for the web platform's trust model.

## Device-to-device Master Key transfer

Signing in on a new device can fetch the MK from an existing device instead of typing the Recovery Key ([src/mk_transfer_crypto.dart](https://github.com/Olace-app/olace-crypto-dart/blob/main/lib/src/mk_transfer_crypto.dart)):

- Ephemeral X25519 exchange; transfer key via HKDF-SHA256 (salt `olace-mk-transfer-v1`, info bound to the transfer id).
- Both devices independently derive a 5-option number challenge from the transcript (salt `olace-mk-sas-v1`). You confirm by tapping the same 3-digit number on both screens. A machine in the middle that substituted a key produces different numbers on each side, and the transfer is abandoned before any ciphertext exists.
- The confirmed number is folded into the GCM AAD (`mk-transfer-v2|<transferId>|sas=<sas>`), so even a lucky guess cannot decrypt the envelope.
