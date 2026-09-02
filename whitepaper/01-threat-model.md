# 1. Threat model

Olace is remote access to your own local AI. A phone talking to your desktop's models, with an optional cloud route and optional encrypted cloud backups. This document series describes what protects your data on each of those paths, what the Olace server can and cannot see, and where the honest limits are. Every cryptographic claim links to public code you can read and to test vectors that pin the exact bytes.

## What we protect against

- **Olace the company reading your conversations.** Cloud backups are encrypted on your device under a Master Key the server never receives (see [03](03-zero-knowledge-backups.md)). The server stores ciphertext it has no key for, and since migration `0057` it has no code path and no permitted row shape for anything else.
- **The relay reading paired traffic.** When your phone reaches your desktop through our relay, frames are end-to-end encrypted between the two devices with forward-secret session keys derived from ephemeral X25519 (see [04](04-e2ee-pairing.md)). The relay moves opaque bytes. This holds against a relay that is honest or merely curious, including a database breach and a passive network observer; the one case it does not cover on its own is a relay that actively substitutes keys while two devices are being paired, which is listed below.
- **A database breach.** Backup content is ciphertext under keys derived from your Master Key. The PIN vault cannot be brute-forced from a database dump alone because its key derivation includes a pepper held outside the database (see [03](03-zero-knowledge-backups.md)).
- **A man in the middle during device pairing and key transfer.** Handshakes are transcript-signed with keys bound to both devices' identities, and Master Key transfer requires a human-verified number match that both devices derive independently (see [04](04-e2ee-pairing.md)).
- **Surveillance through product metrics.** Operator metrics are aggregate counters with bounded enum dimensions, enforced by an ingestion-time allowlist. No metric can carry an identifier or content (see [05](05-metrics-privacy.md)).

## What we do not protect against

- **An actively malicious Olace server at pairing time.** Each device learns its peer's public key from our backend. Today that key is not yet pinned on first use, so a server that was compromised or coerced at the moment you paired two devices could hand each of them a key it controls and read that session. It cannot do this to a session it merely records, it cannot do it after the fact, and it is the same trust model most end-to-end encrypted messengers run on: the provider operates the key directory. The planned mitigation is pin-on-first-use with a visible "security key changed" notice and a comparable fingerprint on the pairing screen (see [08](08-honest-limitations.md)).
- **A compromised device.** Olace runs on your hardware with your data. Malware with your OS privileges can read what you can read. Local data is plaintext at rest on native platforms by design; the device is inside the trust boundary and OS disk encryption is the layer for stolen-hardware risk (see [08](08-honest-limitations.md)).
- **A malicious client build.** If the app or daemon binary you run is hostile, no protocol saves you. The mitigation is this repo: the cryptographic core that protects your data is open, and the closed apps import it verbatim. Reproducible builds are a goal, not a current guarantee.
- **The web platform's trust model.** A web app re-fetches its code from the server on every visit. We reduce the blast radius (the Master Key is never persisted in browser storage), but the web cannot offer the same guarantees as the installed apps (see [08](08-honest-limitations.md)).
- **Traffic metadata.** Encryption hides content, not existence. Timing, sizes and presence are visible to the server and the network (see [08](08-honest-limitations.md)).

## The trust chain

1. **Open crypto core.** [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart) (the app side) and [olace-e2ee-go](https://github.com/Olace-app/olace-e2ee-go) (the daemon side) contain every byte-producing cryptographic operation. The closed apps call these libraries and never reimplement them.
2. **Cross-implementation vectors.** The two independent implementations are pinned to each other by [shared test vectors](../test-vectors/) enforced in both repos' CI. Wire bytes cannot drift silently.
3. **This repo.** Design documentation, the metrics catalog with its sync checker, and the disclosure policy. Claims here reference code and symbols, and where a claim rests on operator behavior instead of code, we say so explicitly.
