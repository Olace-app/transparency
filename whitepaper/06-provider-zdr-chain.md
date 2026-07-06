# 6. Cloud inference and the zero-data-retention chain

Olace's first-party cloud route runs on OpenRouter. Privacy on that route is not a settings page we hope stays checked; it is pinned in code on every request.

## The per-request pin

The backend builds every OpenRouter request with an immutable provider constraint:

```python
OPENROUTER_PROVIDER_PIN = MappingProxyType({"zdr": True, "data_collection": "deny"})
```

`zdr: true` restricts routing to endpoints under OpenRouter's zero-data-retention policy; `data_collection: "deny"` excludes providers that would retain or train on prompts. The pin is applied to chat, tool-calling, research and utility calls alike. There is no code path that sends a first-party cloud request without it.

## Honest scope of the claim

What Olace enforces: the constraint is attached to every request, and OpenRouter routes only to endpoints that accept it. What Olace cannot enforce: the provider's actual server behavior. Retention on those machines is governed by OpenRouter's ZDR contracts with its providers, not by our infrastructure. We state it this way because that is what the code can and cannot prove. OpenRouter's policy: https://openrouter.ai/docs/guides/features/zdr

The backend itself does not log prompts or completions on this route, and does not persist them; conversation content is stored server-side only as `zk1` ciphertext written by your device, and only when cloud backup is on (see [02](02-what-the-server-stores.md)).

## Bring your own key

BYOK requests never touch the Olace backend at all: the app calls your chosen provider directly over HTTPS from your device, and your API key lives in your device's secure storage. What that provider retains is between you and them; Olace adds no curation layer and claims none.

## Search and weather

Tool calls that hit search providers go through a backend cache that is deliberately unattributed: cache keys are derived from the query, entries carry no user or device association, and entries expire by type. Search providers see queries from Olace's servers, not from your IP.
