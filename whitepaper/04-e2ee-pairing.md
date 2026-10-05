# 4. End-to-end encrypted device pairing

Pairing lets your phone use your desktop's models. Traffic between paired devices is end-to-end encrypted whether it travels over your LAN or through the Olace relay. Both implementations are public and pinned to each other by [shared test vectors](../test-vectors/e2ee_vectors.json): [olace-e2ee-go](https://github.com/Olace-app/olace-e2ee-go) runs in the desktop daemon, [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart) in the app.

## Device identity

Each device holds a static X25519 identity keypair. The public key and its SHA-256 fingerprint are registered with the backend per account; the private key never leaves the device (the daemon exposes it to same-user processes on the loopback API behind a local token, which is how the desktop app and the daemon share one identity; another user on the machine or an offline copy of the disk cannot read it).

The backend is the key directory: a device learns its peer's public key from the pair record the backend serves. Each device pins, per pair, the first peer key that completes a verified handshake (trust on first use) and compares every later verified key with it, using a fingerprint it computes itself rather than the one the backend lists. The pin is soft. A key that changes between sessions (a reinstall, or a substitution by a compromised backend) is accepted and the session proceeds, and the device records a notice naming the peer: "<Name> has a new security key. This happens after reinstalling Olace or setting up a new device. Didn't do that? Unpair it." The app shows it as a card at the top of the pairing settings, and `olace status` shows it as a `Security:` row, until it is dismissed or for 14 days. A change back to a key the device already saw for the same pair raises no new notice. Unpairing and pairing again creates a new pair, which starts from a fresh first use. See [08](08-known-limitations.md) for what that means.

On desktop the private key rests in `identity.enc`, AES-256-GCM wrapped with a random 32-byte key held in the OS keystore (libsecret, Keychain, wincred). Headless machines without a keystore fall back to a machine-id-derived key with a logged warning, and are upgraded to the keystore format automatically once one is available. Corrupt identity files are quarantined, never silently overwritten. Code: [e2ee/identity.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/identity.go), [keystore/](https://github.com/Olace-app/olace-e2ee-go/blob/main/keystore/keystore.go).

## Verifying a pair

Two checks let a user confirm that the pinned key is the peer's real key, the first one included:

- **Scanning the pairing code.** The pairing QR code and link that the host shows carry `k`, the first 16 bytes of the SHA-256 fingerprint of the host's key, read from the host's own identity. When the app claims a pair from a scanned code or from a link carrying `k`, the first verified key for that pair is checked against it. A match marks the pair as verified; a mismatch still connects, since the pin is soft, and raises the same new-security-key notice. A pairing code typed by hand carries no key and gets no such check.
- **The security code.** Each pair has a 40-digit code that both devices compute from local data only: the device's own key and the peer key it pinned, never the key the backend lists. Each key contributes a 20-digit half (1024 rounds of SHA-256 over the domain `olace-pair-code-v1` and the key fingerprint, reduced to four 5-digit groups), and the two halves are sorted and joined, so both devices show the same code. It appears under Encryption in the pair's menu in the app and from `olace pair verify <device>`, once the devices have connected securely at least once. Matching codes on both devices mean no one in between, the backend included, substituted a key.

## Session establishment

Two session types, one cipher ([e2ee/crypto.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/crypto.go)):

- **LAN P2P** (`DeriveSessionKey`): X25519 over both the static identity keys and fresh ephemeral keys, concatenated and fed to HKDF-SHA256 with salt `olace-p2p-session-v1`. Binding to the static keys authenticates the devices; the ephemerals freshen each session.
- **Relay** (`DeriveForwardSecretSessionKey`): X25519 over ephemeral keys only, HKDF-SHA256 with salt `olace-paired-e2ee-relay-fs-v2`. Forward secret: compromising a device identity later does not decrypt recorded relay traffic. The backend relays these frames without any key that opens them.

Handshakes are authenticated by HMAC-SHA256 over a canonical transcript of every handshake field (pair id, user id, both device ids, key versions, session id, ephemeral keys, nonces), keyed by an auth key derived from the static-static X25519 secret (salt `olace-p2p-auth-v1`). A relay that alters any field invalidates the signature. Transcript formats: [e2ee/handshake.go](https://github.com/Olace-app/olace-e2ee-go/blob/main/e2ee/handshake.go).

## Frame encryption

Every frame is AES-256-GCM with a random 96-bit nonce and AAD `sessionId|seq|senderKeyVersion`. Receivers enforce strictly increasing sequence numbers, so captured frames cannot be replayed. The envelope format and the decrypt behavior of both implementations are pinned by the shared vectors.

Both directions of a session share one key, and the AAD does not name the sender. A relay can therefore reflect a device's own frame back to it; the frame decrypts, is rejected as an unexpected type, and the session ends. That is a denial of service the relay could achieve anyway by dropping frames, not a read, and no frame type is meaningful in both directions. The current wire format has no direction binding (separate keys per direction, or the sender in the AAD).

## What the relay sees

For an E2EE paired session the backend sees: that a session exists between two of your devices, frame sizes and timing, and the opaque ciphertext. An honest or curious relay, a breached database, or anyone recording the traffic cannot read prompts, responses or file contents. The exception is a relay that was actively malicious at the moment the two devices paired and served each a key it controls, on a pair that was not made by scanning and whose security code nobody compared; [08](08-known-limitations.md) describes that case. Session metadata is what makes routing work; [08](08-known-limitations.md) also covers what metadata implies.
