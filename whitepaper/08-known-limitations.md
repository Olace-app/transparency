# 8. Known limitations

This section lists the boundaries of Olace's design: the properties it does not provide and the trade-offs made deliberately. It is part of the specification, not an appendix.

## The web app has a weaker trust model

An installed app is code obtained once and can be pinned. A web app is code the server delivers on every visit, so a compromised or coerced server could ship JavaScript that reads keys as they are used. No client-side cryptography can fully defend against the party that supplies the client. Olace reduces the exposure on web: the Master Key is never written to browser storage and lives only in page memory for the session, and "Trust this browser" stores only a wrapped MK under a non-extractable WebCrypto key. For the strongest form of the guarantees in this paper, use the desktop or mobile apps.

## Local data is plaintext at rest, by design

On desktop and mobile, conversations, attachments and the search index are stored unencrypted on the device. The device is inside the trust boundary: Olace's encryption protects data from the cloud, Olace included, not from someone holding unlocked hardware. Full-disk encryption (FileVault, BitLocker, LUKS, Android file-based encryption, iOS Data Protection) is the appropriate layer for a lost or stolen device, and app-level encryption on top of it would add key-management failure modes for little gain. Web is the exception, and content there is encrypted in IndexedDB, because browser storage is the least trusted of the platforms.

## Key directory trust during pairing

When two devices pair, each learns the other's public key from the Olace backend. The session is then protected from Olace, from a database breach, and from the network. Each device pins the first key that completes a verified handshake for the pair. What the pin does not cover on its own is a backend that was compromised or coerced at the moment of pairing and served each device a key it controls, because neither device has a prior key to compare against, so the substituted key becomes the pin. A server that only records traffic gains nothing; the attack has to be live, at pairing time, and leaves a substituted key on both devices. Pairing by scanning the host's QR code checks the first key against the fingerprint the code carries, and comparing the pair's 40-digit security code on both devices reveals a substitution at any time (see [04](04-e2ee-pairing.md)). A pair made with a typed code, whose security code nobody compares, has no such check.

This is the model most end-to-end encrypted messengers ship with. The pin is soft: a key that differs from the pinned one is accepted, and the device shows a "has a new security key" notice instead of refusing the connection, because pinning that refuses a changed key would break every pair on an app reinstall, which is the one moment users must not be locked out. A substitution after the first connection is therefore visible, not blocked. The notice clears when dismissed or after 14 days, a change back to a key the device already saw for the pair raises no new notice, and a new pair the backend creates starts from a fresh first use with no notice. The device names shown in pairing come from the backend.

Two related details. Frames share one key in both directions, so a relay can return a device's own frame to it and end the session; that is a denial of service, not a read, and the wire format has no direction binding. And the desktop identity key is readable by any process running as the same OS user on that machine, through the daemon's loopback API; the keystore wrapping protects it from other users and from offline copies of the disk, not from same-user malware, which the compromised-device case in [01](01-threat-model.md) already covers.

## Number-match verification depends on the user

Master Key transfer, and sign-in approval with a key bundle, are only as strong as the tap the user makes. The new device shows one 3-digit number; the device holding the key shows its own number among four decoys, checks the user's tap itself, and releases the key only when the tap matches its own number. A wrong tap ends the transfer. Under a key substitution the two numbers differ, so the protection holds when the user taps the number the new device shows. A user who picks a number without reading the new device's screen picks the key holder's number one time in five and forgoes the man-in-the-middle protection that time. The AAD binding limits the damage of a lucky collision, but the comparison is part of the protocol. The same holds for the pair security code in [04](04-e2ee-pairing.md): it protects only when someone compares it.

## Encryption does not hide metadata

The server necessarily sees that devices exist, when they are online, when sessions open, and how large encrypted frames and backups are. `text_size_bytes` on backups reveals how much a user writes. Olace does not claim resistance to traffic analysis of timing and sizes.

## Recovery requires the user's own keys

Zero-knowledge means there is no recovery desk. A user who loses the Recovery Key, the PIN, and every signed-in device cannot recover their cloud backups, and neither can Olace. Setup states this before backup is enabled. The property is kept deliberately: a recovery path for the user would be a recovery path for Olace and for anyone who could compel it.

## A Sync PIN is guessable by whoever holds both halves

A 6-digit PIN has a million possible values. The vault keeps a database dump useless on its own, because every guess also needs the pepper, which lives outside the database, and the online endpoints lock after ten wrong attempts. A party holding both the database and the pepper, which is Olace itself or someone able to compel it or take over the running service, could still try every PIN for one account offline. It would be a deliberate, per-account search, not access to stored data in bulk. Setting up sync without a PIN removes this path: a Recovery Key cannot be guessed, and a trusted device hands the key over only after a number match the user confirms.

## Binaries are not reproducible

The crypto code and the vectors are public, but the shipped binaries cannot be rebuilt bit-for-bit to prove they contain exactly that code. Builds are not reproducible today. The open core plus dependency pinning is the verification boundary.

## Development fallbacks

The PIN vault pepper and some server keys have development fallbacks so the stack runs locally without provisioned secrets. They log warnings at startup. Production deployments use the environment keyring (`PIN_VAULT_PEPPER_KEYRING_JSON` and related variables); that production runs with real secrets is an operator statement, not something this repo can prove. It is recorded here so that a reader of the code does not have to wonder.

## Limits of verifiability

Three things cannot be demonstrated from public code: that Olace's servers run the code described here, that OpenRouter's providers honor their retention contracts ([06](06-provider-zdr-chain.md)), and that Olace never receives a lawful order. The mitigations are architectural: design the system so that the server holding the data cannot read it, keep the proof of that in public code, and keep the amount of trust a user must extend as small as possible.
