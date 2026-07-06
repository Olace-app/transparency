# 7. Retention and deletion

What the server keeps, for how long, and what deletion actually does. Local copies on your devices are yours and are never touched by server-side retention.

## Encrypted cloud backups

- **While your plan includes cloud backup**: kept until you delete them or delete your account.
- **When a paid plan lapses**: encrypted cloud data enters a 60-day hold (`CLOUD_BACKUP_TIER_LAPSE_RETENTION_DAYS`, default 60), then is pruned. Re-subscribing within the window keeps everything. Your local data is unaffected either way.
- **When you disable backup or delete a conversation**: deletion is queued and executed against both the database rows and the object-store blobs; media deletions retry until confirmed (`media_delete_queue`).
- **Deleted conversations** leave a short-lived tombstone (id only, no content) so your offline devices learn about the deletion instead of resurrecting it, then the tombstone is swept.

## Account deletion

Deleting your account removes your backups, wrapped keys, PIN vault, devices, pairings, push tokens and profile. Aggregate metric rollups contain nothing attributable to remove. Two things survive deliberately: billing records required by tax and accounting law, and the one-way identity hashes that prevent repeated free-credit farming through delete-and-recreate cycles. Neither contains content.

## Ephemeral state

Short-lived operational state, with its lifetime, all server-side:

| State | Lifetime |
|---|---|
| Access tokens | 5 minutes |
| Refresh tokens | 30 days, rotated on use |
| WebSocket auth tickets | 60 seconds |
| Master Key transfer offers | 1 to 4 minutes |
| Device presence records | minutes-scale expiry |
| Notification queue rows | per-row expiry, then swept |
| Pending encryption setup records | short TTL, then expired |

## What is never retained

Prompts and completions on the cloud route (not logged, not stored; see [06](06-provider-zdr-chain.md)), paired-session ciphertext (relayed, never written), raw device identifiers, and plaintext of anything under `zk1`.
