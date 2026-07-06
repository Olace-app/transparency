# 8. Honest limitations

Security documents that only list strengths are marketing. These are the real limits of Olace's design, including the ones we chose on purpose.

## The web app is the weakest platform

An installed app is code you obtained once and can pin. A web app is code the server re-delivers on every visit: a compromised or coerced server could ship JavaScript that exfiltrates keys as you use them, and no client-side cryptography can fully defend against the party that supplies the client. We reduce the blast radius on web: the Master Key is never written to browser storage, living only in page memory per session; "Trust this browser" stores only a wrapped MK under a non-extractable WebCrypto key. But if you want the strong version of our guarantees, use the desktop or mobile apps. We say this plainly because pretending web equals native would be false.

## Local data is plaintext at rest, on purpose

On desktop and mobile, conversations, attachments and the search index are stored unencrypted on your device. The device is inside the trust boundary: Olace's encryption exists to protect you from the cloud (us included), not from someone holding your unlocked hardware. Full-disk encryption (FileVault, BitLocker, LUKS, Android FBE, iOS Data Protection) is the correct layer for a stolen device, and layering app-level crypto on top would add key-management failure modes for little real gain. Web is the exception (content there is encrypted in IndexedDB) precisely because the browser's storage is the least trustworthy of the platforms.

## Number-match verification depends on the human

The MK transfer and pairing SAS flow is only as strong as the person comparing the numbers. Someone who taps a number without looking at the other screen waives the man-in-the-middle protection. The AAD binding limits the damage of a lucky collision, but attention is part of the protocol.

## Encryption does not hide metadata

The server necessarily sees that your devices exist, when they are online, when sessions open, and how large encrypted frames and backups are. `text_size_bytes` on backups leaks how much you write. Traffic analysis of timing and sizes is a real field of study, and we do not claim resistance to it.

## You can lose your data

Zero-knowledge means no recovery desk. If you lose the Recovery Key, the PIN, and every signed-in device, your cloud backups are ciphertext forever. We surface this loudly during setup; it remains the sharpest edge of the design and we keep it anyway, because a recovery path for you would be a recovery path for us and for anyone who compels us.

## Binaries are not yet reproducible

You can read the crypto code and verify the vectors, but you cannot yet rebuild our shipped binaries bit-for-bit to prove they contain exactly that code. Reproducible builds are the known fix and a stated goal, not a current property. Until then, the open core plus dependency pinning is the verification boundary.

## Dev fallbacks exist and production must not use them

The PIN vault pepper and some server keys have insecure development fallbacks so the stack runs locally without secrets provisioned. They log loud warnings. Production deployments require the real environment keyring (`PIN_VAULT_PEPPER_KEYRING_JSON` and friends); the operator statement that production runs with real secrets is exactly that, an operator statement. This is noted here so no one has to discover it in the code and wonder.

## Things we simply cannot prove to you

That our servers run the code we say they run, that OpenRouter's providers honor their retention contracts ([06](06-provider-zdr-chain.md)), and that we never receive a lawful order. Our mitigations are architectural: design the system so the server holding your data cannot read it, keep the proof of that in public code, and keep the amount of trust you must extend as small as we can make it.
