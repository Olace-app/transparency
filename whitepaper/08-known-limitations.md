# 8. Known limitations

This section lists the boundaries of Olace's design: the properties it does not provide, the trade-offs made deliberately, and the work that is planned. It is part of the specification, not an appendix.

## The web app has a weaker trust model

An installed app is code obtained once and can be pinned. A web app is code the server delivers on every visit, so a compromised or coerced server could ship JavaScript that reads keys as they are used. No client-side cryptography can fully defend against the party that supplies the client. Olace reduces the exposure on web: the Master Key is never written to browser storage and lives only in page memory for the session, and "Trust this browser" stores only a wrapped MK under a non-extractable WebCrypto key. For the strongest form of the guarantees in this paper, use the desktop or mobile apps.

## Local data is plaintext at rest, by design

On desktop and mobile, conversations, attachments and the search index are stored unencrypted on the device. The device is inside the trust boundary: Olace's encryption protects data from the cloud, Olace included, not from someone holding unlocked hardware. Full-disk encryption (FileVault, BitLocker, LUKS, Android file-based encryption, iOS Data Protection) is the appropriate layer for a lost or stolen device, and app-level encryption on top of it would add key-management failure modes for little gain. Web is the exception, and content there is encrypted in IndexedDB, because browser storage is the least trusted of the platforms.

## Key directory trust during pairing

When two devices pair, each learns the other's public key from the Olace backend. The session is then protected from Olace, from a database breach, and from the network. What it does not yet cover is a backend that was compromised or coerced at the moment of pairing and served each device a key it controls, because neither device has a prior key to compare against and no fingerprint is shown for the user to check. A server that only records traffic gains nothing; the attack has to be live, at pairing time, and leaves a substituted key on both devices.

This is the model most end-to-end encrypted messengers ship with, and Olace starts from the same point: pinning that refuses a changed key would break every pair on an app reinstall, which is the one moment users must not be locked out. The planned design keeps pairs working and makes substitution visible: each device remembers the first key it saw for a pair, shows a one-time "security key changed" notice on both devices when it differs (expected after a reinstall, worth attention otherwise), and shows a short fingerprint on the pairing screen for anyone who wants to compare. Until that ships, this section is the disclosure.

Two related details. Frames share one key in both directions, so a relay can return a device's own frame to it and end the session; that is a denial of service, not a read, and direction binding is scheduled for the next wire version. And the desktop identity key is readable by any process running as the same OS user on that machine, through the daemon's loopback API; the keystore wrapping protects it from other users and from offline copies of the disk, not from same-user malware, which the compromised-device case in [01](01-threat-model.md) already covers.

## Number-match verification depends on the user

The Master Key transfer and pairing SAS flow is only as strong as the comparison the user makes. Confirming a number without checking the other screen forgoes the man-in-the-middle protection. The AAD binding limits the damage of a lucky collision, but the comparison is part of the protocol.

## Encryption does not hide metadata

The server necessarily sees that devices exist, when they are online, when sessions open, and how large encrypted frames and backups are. `text_size_bytes` on backups reveals how much a user writes. Olace does not claim resistance to traffic analysis of timing and sizes.

## Recovery requires the user's own keys

Zero-knowledge means there is no recovery desk. A user who loses the Recovery Key, the PIN, and every signed-in device cannot recover their cloud backups, and neither can Olace. Setup states this before backup is enabled. The property is kept deliberately: a recovery path for the user would be a recovery path for Olace and for anyone who could compel it.

## Binaries are not yet reproducible

The crypto code and the vectors are public, but the shipped binaries cannot yet be rebuilt bit-for-bit to prove they contain exactly that code. Reproducible builds are a stated goal, not a current property. Until then, the open core plus dependency pinning is the verification boundary.

## Development fallbacks

The PIN vault pepper and some server keys have development fallbacks so the stack runs locally without provisioned secrets. They log warnings at startup. Production deployments use the environment keyring (`PIN_VAULT_PEPPER_KEYRING_JSON` and related variables); that production runs with real secrets is an operator statement, not something this repo can prove. It is recorded here so that a reader of the code does not have to wonder.

## Limits of verifiability

Three things cannot be demonstrated from public code: that Olace's servers run the code described here, that OpenRouter's providers honor their retention contracts ([06](06-provider-zdr-chain.md)), and that Olace never receives a lawful order. The mitigations are architectural: design the system so that the server holding the data cannot read it, keep the proof of that in public code, and keep the amount of trust a user must extend as small as possible.
