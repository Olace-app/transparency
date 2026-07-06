# 2. What the server stores

Everything the Olace backend persists, by data class. "Server can read" means the running service holds a key or code path that yields plaintext. Since migration `0057_zero_knowledge_only` the backup tables carry a database CHECK constraint (`enc_mode = 'zk1'`) and the write layer rejects anything else, so "no" below is enforced by row shape, not just by code review.

| Data class | At rest | Server can read? | Notes |
|---|---|---|---|
| Conversation backups (`conversation_backups.payload_enc`) | `zk1` envelope, AES-256-GCM under a per-conversation key derived from your Master Key | **No** | The server never holds the MK. Plaintext checkpoints are rejected at the API and by a CHECK constraint. |
| Research context (`research_context_enc`) | `zk1` envelope | **No** | Same key hierarchy, separate purpose string. |
| Media backups (`media_backups` blobs in object storage) | `zk1` bytes, AES-256-GCM per attachment | **No** | Encrypted client-side before upload. |
| Media file names and MIME types (`file_name_enc`, `mime_type_enc`) | `zk1`-derived envelope, field name bound into the AAD | **No** | A file-name ciphertext cannot be replayed as a MIME type. |
| Project backups (`project_backups.payload_enc`) | `zk1` envelope | **No** | |
| Wrapped Master Key (`user_encryption_keys.wrapped_mk`) | AES-256-GCM under a key derived from your Recovery Key | **No** | The Recovery Key exists only on paper and in your devices. |
| PIN vault (`pin_vault`) | Encrypted Recovery Key, Argon2 salt and params, a SHA-256 hash of the auth tag, pepper key id, attempt counter | **No** | The vault key requires the PIN, and its derivation includes a pepper held outside the database. See [03](03-zero-knowledge-backups.md). |
| Text size metadata (`text_size_bytes`) | Integer | **Yes** | Used for quota accounting. Sizes leak coarse information about how much you write; content does not. |
| Settings profile (`user_sync_profiles.profile_enc`) | Encrypted server-side with a server-held key | **Yes, by design** | App settings and sync bookkeeping, not conversation content. Server-side encryption here protects against database exposure, not against Olace. Documented as the deliberate exception it is. |
| Account identity (phone number, email) | Encrypted server-side with a server-held key | **Yes, by design** | Needed to sign you in, send OTPs, and meet legal obligations. Never placed in the zero-knowledge profile blob. |
| Device records, pairings, presence | Rows with HMAC-canonicalized device ids (`didv1_...`, see [reference/device_id.py](../reference/device_id.py)) | **Yes** | Raw hardware identifiers are never stored; the HMAC form is not reversible to the OS id. |
| Notification queue (`notification_queue.payload_json`) | Plaintext JSON with a per-row expiry | **Yes** | Delivery scaffolding for offline devices (for example a sign-in approval prompt). Carries event data, never conversation content. Rows expire and are swept. |
| Feedback and bug reports (`feedback_submissions`) | Plaintext | **Yes, intentionally** | You are writing TO support. The compose screen is explicit about this. |
| Push tokens | Platform push tokens | **Yes** | Required to deliver push notifications; deleted with the device record. |
| Billing and entitlements | Plan, credit ledger, payment-processor references | **Yes** | Payment card data never touches Olace; it stays with the merchant of record. |
| Operator metrics (`metric_rollup`) | Aggregate counters with bounded enum dimensions | **Yes** | Cannot contain identifiers or content by construction. See [05](05-metrics-privacy.md). |

## What does not exist on the server

- No plaintext conversation or message table. Content exists server-side only as `zk1` ciphertext, and only if you enabled cloud backup.
- No server-side decryption path for backups. The legacy mode that allowed it was removed (code and schema) before launch; the CHECK constraints above are the durable record of that removal.
- No prompt or completion logging on the cloud inference route. Requests are relayed to the provider with zero-data-retention pinned per request (see [06](06-provider-zdr-chain.md)).
- No raw device identifiers and no raw IP addresses in application tables. One qualifier so this claim survives a code read: sign-in approval challenges store a one-way hash of the requesting IP (`login_approval_challenges.request_ip_hash`), used to tell you whether an approval request resembles earlier ones from the same network. The row expires with the challenge and the hash is not reversible to an address.

## Chat traffic (not storage)

Chat requests to your own hardware run locally or device-to-device encrypted. Cloud-routed chat passes through the backend in TLS-protected transport and is orchestrated in memory; it is not written to conversation storage server-side. Cloud backup, when enabled, is written by your device as `zk1` ciphertext through the sync API.
