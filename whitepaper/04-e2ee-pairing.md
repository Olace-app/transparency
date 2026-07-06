# 4. End-to-end encrypted device pairing

Pairing lets your phone use your desktop's models. Traffic between paired devices is end-to-end encrypted whether it travels over your LAN or through the Olace relay. Both implementations are public and pinned to each other by [shared test vectors](../test-vectors/e2ee_vectors.json): [olace-e2ee-go](https://github.com/Olace-app/olace-e2ee-go) runs in the desktop daemon, [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart) in the app.

## Device identity

Each device holds a static X25519 identity keypair. The public key and its SHA-256 fingerprint are registered with the backend per account; the private key never leaves the device.

On desktop the private key rests in `identity.enc`, AES-256-GCM wrapped with a random 32-byte key held in the OS keystore (libsecret, Keychain, wincred). Headless machines without a keystore fall back to a machine-id-derived key with a logged warning, and are upgraded to the keystore format automatically once one is available. Corrupt identity files are quarantined, never silently overwritten. Code: [e2ee/identity.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/identity.go), [keystore/](https://github.com/Olace-app/olace-e2ee-go/blob/main/keystore/keystore.go).

## Session establishment

Two session types, one cipher ([e2ee/crypto.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/crypto.go)):

- **LAN P2P** (`DeriveSessionKey`): X25519 over both the static identity keys and fresh ephemeral keys, concatenated and fed to HKDF-SHA256 with salt `olace-p2p-session-v1`. Binding to the static keys authenticates the devices; the ephemerals freshen each session.
- **Relay** (`DeriveForwardSecretSessionKey`): X25519 over ephemeral keys only, HKDF-SHA256 with salt `olace-paired-e2ee-relay-fs-v2`. Forward secret: compromising a device identity later does not decrypt recorded relay traffic. The backend relays these frames without any key that opens them.

Handshakes are authenticated by HMAC-SHA256 over a canonical transcript of every handshake field (pair id, user id, both device ids, key versions, session id, ephemeral keys, nonces), keyed by an auth key derived from the static-static X25519 secret (salt `olace-p2p-auth-v1`). A relay that alters any field invalidates the signature. Transcript formats: [e2ee/handshake.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/handshake.go).

## Frame encryption

Every frame is AES-256-GCM with a random 96-bit nonce and AAD `sessionId|seq|senderKeyVersion`. Receivers enforce strictly increasing sequence numbers, so captured frames cannot be replayed. The envelope format and the decrypt behavior of both implementations are pinned by the shared vectors.

## What the relay sees

For an E2EE paired session the backend sees: that a session exists between two of your devices, frame sizes and timing, and the opaque ciphertext. It cannot read prompts, responses or file contents. Session metadata is what makes routing work; [08](08-honest-limitations.md) covers what metadata implies.
