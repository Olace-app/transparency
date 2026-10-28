"""Metrics catalog — the single source of truth for the Olace metrics system.

LOCKSTEP CONTRACT
=================
Metric names, dimension keys, dimension values, and histogram bucket labels
defined here are mirrored byte-for-byte in:
  * Daemon  — Daemon/internal/metrics/catalog.go
  * Flutter — Flutter/lib/constants/metric_constants.dart
Any edit here REQUIRES a matching edit in both. The backend aggregates rolled-up
counters by exact string equality of (metric, dims_json); a single drifted
string ("need_tool" vs "needs_tool", "1000" vs "1000.0") silently splits one
logical counter into two rows with no error anywhere.

This module is pure constants + pure helpers — it imports nothing from the rest
of the app (no Redis, no DB), so it is safe to import from anywhere, including
tests that pin the canonical wire format.

PRIVACY
=======
Every dimension value below is a bounded enum. No dimension ever carries an
identifier (device id, user id, conversation id, IP, phone/email) or any user
content. The METRIC_DIM_SPEC allowlist is what makes that guarantee enforceable
at ingestion: a counter whose metric or dims are not in the spec is dropped.
"""
from __future__ import annotations

import json
import re

M_WS_CONNECT = "ws.connect"
M_RELAY_EVENT = "relay.event"
M_TUNNEL_EVENT = "tunnel.event"
M_CHAT_CLASSIFY_DECISION = "chat.classify_decision"
M_CHAT_TOOL_EXECUTION = "chat.tool_execution"
M_CHAT_TOOL_LATENCY = "chat.tool_latency"
M_SEARCH_DIGEST = "search.digest"
M_SEARCH_ALIAS = "search.alias"
M_OPENROUTER_CACHE = "openrouter.cache"
M_CHAT_TTFT = "chat.ttft"
M_CHAT_TTFT_FIRST = "chat.ttft_first"
M_CHAT_PEEK_HANDOFF_OVERTURN = "chat.peek_handoff_overturn"
M_CHAT_REACT_FALLBACK = "chat.react_fallback"
M_CHAT_CONTEXT_OVERFLOW_RETRY = "chat.context_overflow_retry"
M_INFRA_DB_POOL_WAIT = "infra.db_pool_wait"
M_INFRA_S3_OP = "infra.s3_op"
M_INFRA_PUSH = "infra.push"
M_INFRA_RATE_LIMIT_REJECT = "infra.rate_limit_reject"
M_INFRA_RATE_LIMIT_FALLBACK = "infra.rate_limit_fallback"
M_INFRA_EXA_QUOTA_BREACH = "infra.exa_quota_breach"
M_AUTH_OTP = "auth.otp"
M_AUTH_GOOGLE = "auth.google"
M_AUTH_TOKEN_REFRESH = "auth.token_refresh"
M_META_REPORTS_RECEIVED = "meta.reports_received"
M_PAIR_FINALIZE = "pair.finalize"
M_ABUSE_ENFORCEMENT = "abuse.enforcement"
M_CHAT_CLOUD_MODEL = "chat.cloud_model"
M_INFRA_HTTP_5XX = "infra.http_5xx"
M_BILLING_WEBHOOK = "billing.webhook"
M_BILLING_CREDIT_SETTLE = "billing.credit_settle"
M_CHAT_PROVIDER_ERROR = "chat.provider_error"
M_CHAT_STREAM_TERMINAL = "chat.stream_terminal"
M_TTS_UNIT = "tts.unit"
M_TTS_PROVIDER = "tts.provider"
M_TTS_COST_MICROUSD = "tts.cost_microusd"

M_CHAT_SECURITY_MODE = "chat.security_mode"
M_CHAT_ROUTE = "chat.route"
M_CHAT_TRANSPORT_RESOLUTION = "chat.transport_resolution"
M_PEEK_OUTCOME = "peek.outcome"
M_PEEK_GUARD_OVERTURN = "peek.guard_overturn"
M_PEEK_CUTOFF_HANDOFF = "peek.cutoff_handoff"
M_CTX_TRUNCATION = "ctx.truncation"
M_CTX_HISTORY_EVICTION = "ctx.history_eviction"
M_DEVICE_VRAM_DETECTION = "device.vram_detection"
M_DEVICE_VRAM_TIER = "device.vram_tier"
M_LOCAL_TTFT = "local.ttft"
M_LOCAL_TTFT_FIRST = "local.ttft_first"
M_LOCAL_OOM_RETRY = "local.oom_retry"
M_NET_SERVICE_RECONNECT = "net.service_reconnect"
M_CHAT_TURN_OUTCOME = "chat.turn_outcome"
M_CHAT_IMAGE_GENERATION = "chat.image_generation"
M_CHAT_IMAGE_INPUT = "chat.image_input"
M_ONBOARDING_MK_TRANSFER = "onboarding.mk_transfer"
M_LOCAL_THROUGHPUT = "local.throughput"
M_SYNC_OPERATION = "sync.operation"
M_LOOP_GUARD_TRIP = "local.loop_guard_trip"
M_APP_CRASH = "app.crash"
M_PAIRED_TTFT = "paired.ttft"
M_ONBOARDING_STEP = "onboarding.step"
M_BILLING_CHECKOUT = "billing.checkout"
M_APP_UPDATE = "app.update"
M_DAEMON_DEPLOY = "daemon.deploy"
M_LOCAL_SETUP = "local.setup"

M_RELAY_TTFT = "relay.ttft"
M_RELAY_TTFT_FIRST = "relay.ttft_first"
M_RELAY_THROUGHPUT = "relay.throughput"
M_RELAY_VRAM_RETRY = "relay.vram_retry"
M_RELAY_WATCHDOG_FIRE = "relay.watchdog_fire"
M_RELAY_TRANSPORT = "relay.transport"
M_TUNNEL_RECONNECT = "tunnel.reconnect"
M_TUNNEL_BACKOFF_DEPTH = "tunnel.backoff_depth"
M_TUNNEL_HEARTBEAT_STALE_CLOSE = "tunnel.heartbeat_stale_close"
M_MODEL_PULL = "model.pull"
M_PROVIDER_AUTO_REVIVE = "provider.auto_revive"
M_PROVIDER_OPTIMIZE = "provider.optimize"
M_CTX_HALVE_NUMCTX = "ctx.halve_numctx"
M_DAEMON_ACTIVE = "daemon.active"
M_CRYPTO_E2EE_HANDSHAKE = "crypto.e2ee_handshake"
M_BRIDGE_REQUEST = "bridge.request"
M_BRIDGE_TTFT = "bridge.ttft"
M_PAIRED_HOST_TTFT = "paired.host_ttft"
M_CTX_FORMULA_FIT = "ctx.formula_fit"
M_CTX_HW_FIT = "ctx.hw_fit"
M_CTX_CLAMP = "ctx.clamp"
M_CTX_PREFILL_SPEED = "ctx.prefill_speed"

DIM_PLATFORM = "platform"
DIM_APP_VERSION = "app_version"
DIM_DAEMON_VERSION = "daemon_version"

LE_LATENCY_BOUNDS_MS = (200, 500, 1000, 2000, 5000, 10000)
LE_THROUGHPUT_BOUNDS_TPS = (5, 10, 20, 40, 80)
LE_BACKOFF_BOUNDS_MS = (2000, 5000, 10000, 20000)
LE_RATIO_BOUNDS_PCT = (40, 60, 80, 95, 110, 130, 160, 200, 300, 500)
LE_CACHE_SHARE_BOUNDS_PCT = (0, 10, 25, 50, 75, 90)
LE_PREFILL_BOUNDS_TPS = (50, 150, 400, 1000, 3000)


def _labels(bounds: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(str(b) for b in bounds) + ("inf",)


LE_LATENCY_LABELS = _labels(LE_LATENCY_BOUNDS_MS)
LE_THROUGHPUT_LABELS = _labels(LE_THROUGHPUT_BOUNDS_TPS)
LE_BACKOFF_LABELS = _labels(LE_BACKOFF_BOUNDS_MS)
LE_RATIO_LABELS = _labels(LE_RATIO_BOUNDS_PCT)
LE_PREFILL_LABELS = _labels(LE_PREFILL_BOUNDS_TPS)
LE_CACHE_SHARE_LABELS = _labels(LE_CACHE_SHARE_BOUNDS_PCT)

METRIC_BUCKETS: dict[str, tuple[int, ...]] = {
    M_CHAT_TOOL_LATENCY: LE_LATENCY_BOUNDS_MS,
    M_SEARCH_DIGEST: LE_LATENCY_BOUNDS_MS,
    M_OPENROUTER_CACHE: LE_CACHE_SHARE_BOUNDS_PCT,
    M_CHAT_TTFT: LE_LATENCY_BOUNDS_MS,
    M_CHAT_TTFT_FIRST: LE_LATENCY_BOUNDS_MS,
    M_INFRA_DB_POOL_WAIT: LE_LATENCY_BOUNDS_MS,
    M_RELAY_TTFT: LE_LATENCY_BOUNDS_MS,
    M_RELAY_TTFT_FIRST: LE_LATENCY_BOUNDS_MS,
    M_LOCAL_TTFT: LE_LATENCY_BOUNDS_MS,
    M_LOCAL_TTFT_FIRST: LE_LATENCY_BOUNDS_MS,
    M_BRIDGE_TTFT: LE_LATENCY_BOUNDS_MS,
    M_PAIRED_TTFT: LE_LATENCY_BOUNDS_MS,
    M_PAIRED_HOST_TTFT: LE_LATENCY_BOUNDS_MS,
    M_RELAY_THROUGHPUT: LE_THROUGHPUT_BOUNDS_TPS,
    M_LOCAL_THROUGHPUT: LE_THROUGHPUT_BOUNDS_TPS,
    M_TUNNEL_BACKOFF_DEPTH: LE_BACKOFF_BOUNDS_MS,
    M_CTX_FORMULA_FIT: LE_RATIO_BOUNDS_PCT,
    M_CTX_HW_FIT: LE_RATIO_BOUNDS_PCT,
    M_CTX_PREFILL_SPEED: LE_PREFILL_BOUNDS_TPS,
}


def _le_labels_for(metric: str) -> frozenset[str]:
    return frozenset(_labels(METRIC_BUCKETS[metric]))


ROUTE = frozenset({"local", "paired", "cloud"})
TRANSPORT = frozenset({"lan_p2p", "relay"})
TRANSPORT_REASON = frozenset(
    {
        "hot",
        "ping_ok",
        "probe_ok",
        "home_known",
        "web",
        "subwindow",
        "lan_unavailable",
        "handshake_blocked",
        "recently_unreachable",
        "network_changed",
        "ping_failed",
        "probe_unproven",
        "probe_timeout",
        "probe_error",
        "lan_not_preferred",
    }
)
BRIDGE_TRANSPORT = frozenset({"local", "lan_p2p", "relay"})
BRIDGE_OUTCOME = frozenset(
    {
        "success",
        "cancelled",
        "invalid_request",
        "unauthorized",
        "not_found",
        "forbidden",
        "rate_limited",
        "host_offline",
        "timeout",
        "provider_error",
        "internal",
    }
)
PROVIDER = frozenset({"ollama", "lmstudio", "llamacpp"})
CLOUD_KEY = frozenset({"olace", "byok"})
SECURITY_MODE = frozenset({"standard", "max_privacy"})
PLATFORM = frozenset({"ios", "android", "linux", "windows", "macos", "web", "unknown"})
BOOL = frozenset({"true", "false"})
TIER = frozenset(
    {"light", "standard", "performance", "advanced", "power", "pro", "ultra", "unknown"}
)
VRAM_DETECTION_SOURCE = frozenset({"daemon", "flutter_fallback", "unknown"})
LOOP_STREAM = frozenset({"visible", "thought"})
LOOP_TIER = frozenset({"short", "block", "budget"})
TOOL = frozenset(
    {
        "web_search",
        "image_search",
        "show_photos",
        "get_weather",
        "find_places",
        "extract_page",
        "deep_research",
        "list_project_files",
        "search_project_files",
        "read_file_chunk",
        "device_pairing",
        "model_hub",
        "setup_local_ai",
        "olace_help",
        "execute_python",
        "create_document",
        "edit_document",
        "scholarly_search",
        "create_image",
        "geocode_time",
        "map_card",
    }
)
LIMITER = frozenset(
    {
        "otp_request",
        "otp_verify",
        "login",
        "logout",
        "relay_open",
        "relay_forward",
        "exa_burst",
        "p2p_rate",
        "metrics_report",
        "openrouter_chat",
        "openrouter_image",
        "openrouter_utility",
        "openrouter_reader",
        "openrouter_speech",
        "chat_fair_use_burst",
        "content_pack_invalidate",
        "refresh",
        "ws_ticket",
        "ws_handshake",
        "recovery_verify",
        "identity_change",
        "pin_vault",
        "chat_start",
        "sync",
        "pairing",
        "text",
        "tts",
    }
)
CLASSIFY_DECISION = frozenset({"direct", "need_tool", "cutoff", "done"})
PEEK_DECISION = frozenset(
    {"direct_answer", "need_tool", "tool_directive", "cutoff", "error"}
)
PEEK_VARIANT = frozenset(
    {"large_local", "small_local", "paired_lan", "paired_relay", "daemon"}
)
BLOCK_TYPE = frozenset(
    {"other_files", "research_files", "attached_files", "project_files", "attachments"}
)
SUCCESS_ERROR = frozenset({"success", "error"})

APP_CRASH_FAULT = frozenset({"widget", "async"})
ONBOARDING_STEP = frozenset({"sign_in", "trial", "sync", "pair", "done"})
ONBOARDING_EVENT = frozenset({"shown", "completed", "skipped", "resumed"})
CHECKOUT_OUTCOME = frozenset(
    {"opened", "launched", "completed", "pending", "cancelled", "failed", "elsewhere"}
)
APP_SURFACE = frozenset({"leader", "subwindow"})
IMAGE_GEN_OUTCOME = frozenset({"success", "error", "cancelled"})
ROUTE_GROUP = frozenset(
    {
        "auth",
        "chat",
        "sync",
        "billing",
        "pairing",
        "models",
        "p2p",
        "metrics",
        "webhooks",
        "ops",
        "other",
    }
)
WEBHOOK_PROVIDER = frozenset({"polar", "revenuecat"})
WEBHOOK_OUTCOME = frozenset({"ok", "invalid_signature", "error", "ignored"})
PROVIDER_ERROR_CLASS = frozenset({"rate_limited", "service_unavailable", "other"})
STREAM_TERMINAL = frozenset({"done", "client_disconnect", "error", "refused"})
TURN_OUTCOME = frozenset({"completed", "error", "cancelled"})
TURN_ERROR_KIND = frozenset(
    {
        "limit", "outdated", "auth", "model_missing", "memory", "context",
        "model_output", "unreachable", "connection", "runtime_error",
        "provider", "other",
    }
)
APP_UPDATE_STEP = frozenset({"download", "install"})
APP_UPDATE_OUTCOME = frozenset(
    {"ok", "failed", "verify_failed", "disk_space", "cancelled", "not_newer"}
)
DAEMON_DEPLOY_TRIGGER = frozenset({"upgrade", "outdated"})
DAEMON_DEPLOY_OUTCOME = frozenset({"ok", "swap_failed", "health_failed"})
LOCAL_SETUP_STEP = frozenset(
    {"start", "runtime", "server", "model", "verify", "done", "first_reply"}
)
LOCAL_SETUP_OUTCOME = frozenset({"started", "ok", "failed", "cancelled"})
PAIR_OUTCOME = frozenset({"success", "stale", "self_pair", "error", "plan_limit", "invalid"})
ABUSE_ACTION = frozenset({"flagged", "suspended"})
MODEL_FAMILY = frozenset(
    {
        "glm",
        "gemma",
        "qwen",
        "kimi",
        "deepseek",
        "llama",
        "mistral",
        "gpt_oss",
        "minimax",
        "step",
        "other",
    }
)
LOCAL_MODEL_FAMILY = frozenset(
    {"llama", "qwen", "gemma", "deepseek", "mistral", "phi", "other"}
)
MODEL_SIZE_BUCKET = frozenset({"lt2", "2_4", "4_8", "8plus"})
GPU_VENDOR = frozenset({"nvidia", "amd", "apple", "intel", "other"})
TTS_UNIT_OUTCOME = frozenset({"success", "upstream", "timeout"})
TTS_PROVIDER = frozenset({"deepinfra", "together", "other", "unknown"})

METRIC_DIM_SPEC: dict[str, dict[str, frozenset[str]]] = {
    M_WS_CONNECT: {"kind": frozenset({"chat", "device", "desktop"})},
    M_RELAY_EVENT: {
        "outcome": frozenset(
            {"error", "drop", "timeout", "owner_mismatch", "congestion"}
        )
    },
    M_TUNNEL_EVENT: {
        "kind": frozenset(
            {"stale", "lease_conflict", "displaced", "receive_timeout", "lease_steal"}
        )
    },
    M_CHAT_CLASSIFY_DECISION: {"decision": CLASSIFY_DECISION, "route": ROUTE},
    M_CHAT_TOOL_EXECUTION: {
        "tool": TOOL,
        "outcome": frozenset({"success", "error", "empty", "timeout"}),
    },
    M_CHAT_TOOL_LATENCY: {"tool": TOOL, "le": _le_labels_for(M_CHAT_TOOL_LATENCY)},
    M_SEARCH_ALIAS: {"outcome": frozenset({"generated", "hit"})},
    M_OPENROUTER_CACHE: {
        "outcome": frozenset({"hit", "miss", "unknown"}),
        "le": _le_labels_for(M_OPENROUTER_CACHE),
    },
    M_SEARCH_DIGEST: {
        "kind": frozenset({"card", "page"}),
        "outcome": frozenset(
            {
                "success", "fallback", "timeout", "length_retry", "skipped", "queued",
                "deadline", "partial",
            }
        ),
        "le": _le_labels_for(M_SEARCH_DIGEST),
    },
    M_CHAT_TTFT: {"route": ROUTE, "le": _le_labels_for(M_CHAT_TTFT)},
    M_CHAT_TTFT_FIRST: {"route": ROUTE, "le": _le_labels_for(M_CHAT_TTFT_FIRST)},
    M_CHAT_PEEK_HANDOFF_OVERTURN: {},
    M_CHAT_REACT_FALLBACK: {},
    M_CHAT_CONTEXT_OVERFLOW_RETRY: {
        "path": frozenset({"direct_reply", "agent", "deep_research"})
    },
    M_INFRA_DB_POOL_WAIT: {"le": _le_labels_for(M_INFRA_DB_POOL_WAIT)},
    M_INFRA_S3_OP: {
        "op": frozenset({"put", "get", "delete", "delete_objects"}),
        "outcome": frozenset({"success", "error"}),
    },
    M_INFRA_PUSH: {
        "channel": frozenset({"fcm", "apns", "smtp"}),
        "outcome": frozenset({"sent", "failed"}),
    },
    M_INFRA_RATE_LIMIT_REJECT: {"limiter": LIMITER},
    M_INFRA_RATE_LIMIT_FALLBACK: {"limiter": LIMITER},
    M_INFRA_EXA_QUOTA_BREACH: {},
    M_AUTH_OTP: {
        "channel": frozenset({"sms", "email"}),
        "action": frozenset({"send", "verify"}),
        "outcome": frozenset({"ok", "rejected", "expired", "error"}),
    },
    M_AUTH_GOOGLE: {
        "step": frozenset({"start", "callback", "exchange"}),
        "outcome": frozenset({"ok", "rejected", "error"}),
    },
    M_AUTH_TOKEN_REFRESH: {"outcome": frozenset({"ok", "rejected", "error"})},
    M_META_REPORTS_RECEIVED: {"source": frozenset({"flutter", "daemon"})},
    M_PAIR_FINALIZE: {"outcome": PAIR_OUTCOME},
    M_ABUSE_ENFORCEMENT: {"action": ABUSE_ACTION},
    M_CHAT_CLOUD_MODEL: {"family": MODEL_FAMILY},
    M_INFRA_HTTP_5XX: {"route_group": ROUTE_GROUP},
    M_BILLING_WEBHOOK: {"provider": WEBHOOK_PROVIDER, "outcome": WEBHOOK_OUTCOME},
    M_BILLING_CREDIT_SETTLE: {"outcome": SUCCESS_ERROR},
    M_CHAT_PROVIDER_ERROR: {"class": PROVIDER_ERROR_CLASS},
    M_CHAT_STREAM_TERMINAL: {"outcome": STREAM_TERMINAL},
    M_TTS_UNIT: {"outcome": TTS_UNIT_OUTCOME},
    M_TTS_PROVIDER: {"provider": TTS_PROVIDER},
    M_TTS_COST_MICROUSD: {"provider": TTS_PROVIDER},
    M_CHAT_SECURITY_MODE: {"mode": SECURITY_MODE},
    M_CHAT_ROUTE: {
        "route": ROUTE,
        "transport": TRANSPORT,
        "provider": PROVIDER,
        "cloud_key": CLOUD_KEY,
    },
    M_CHAT_TRANSPORT_RESOLUTION: {
        "transport": TRANSPORT,
        "reason": TRANSPORT_REASON,
    },
    M_PEEK_OUTCOME: {"variant": PEEK_VARIANT, "decision": PEEK_DECISION},
    M_PEEK_GUARD_OVERTURN: {"variant": PEEK_VARIANT},
    M_PEEK_CUTOFF_HANDOFF: {"suppressed": BOOL},
    M_CTX_TRUNCATION: {"block_type": BLOCK_TYPE},
    M_CTX_HISTORY_EVICTION: {},
    M_DEVICE_VRAM_DETECTION: {"source": VRAM_DETECTION_SOURCE},
    M_DEVICE_VRAM_TIER: {"tier": TIER, "kv_halved": BOOL},
    M_LOCAL_TTFT: {
        "provider": PROVIDER,
        "state": frozenset({"cold", "hot"}),
        "le": _le_labels_for(M_LOCAL_TTFT),
    },
    M_LOCAL_TTFT_FIRST: {
        "provider": PROVIDER,
        "le": _le_labels_for(M_LOCAL_TTFT_FIRST),
    },
    M_LOCAL_OOM_RETRY: {"provider": PROVIDER},
    M_LOOP_GUARD_TRIP: {
        "provider": PROVIDER,
        "stream": LOOP_STREAM,
        "tier": LOOP_TIER,
    },
    M_NET_SERVICE_RECONNECT: {
        "service": frozenset({"chat_socket", "device_realtime", "desktop_tunnel"}),
        "lifecycle": frozenset({"foreground", "background"}),
    },
    M_CHAT_TURN_OUTCOME: {
        "route": ROUTE,
        "outcome": TURN_OUTCOME,
        "error_kind": TURN_ERROR_KIND,
        "cloud_key": CLOUD_KEY,
    },
    M_APP_UPDATE: {"step": APP_UPDATE_STEP, "outcome": APP_UPDATE_OUTCOME},
    M_DAEMON_DEPLOY: {
        "trigger": DAEMON_DEPLOY_TRIGGER,
        "outcome": DAEMON_DEPLOY_OUTCOME,
    },
    M_LOCAL_SETUP: {
        "step": LOCAL_SETUP_STEP,
        "outcome": LOCAL_SETUP_OUTCOME,
        "provider": PROVIDER,
    },
    M_CHAT_IMAGE_GENERATION: {"outcome": IMAGE_GEN_OUTCOME, "cloud_key": CLOUD_KEY},
    M_CHAT_IMAGE_INPUT: {"route": ROUTE},
    M_ONBOARDING_MK_TRANSFER: {"outcome": SUCCESS_ERROR},
    M_LOCAL_THROUGHPUT: {
        "provider": PROVIDER,
        "le": _le_labels_for(M_LOCAL_THROUGHPUT),
    },
    M_SYNC_OPERATION: {"outcome": SUCCESS_ERROR},
    M_APP_CRASH: {"fault": APP_CRASH_FAULT, "surface": APP_SURFACE},
    M_ONBOARDING_STEP: {"step": ONBOARDING_STEP, "event": ONBOARDING_EVENT},
    M_BILLING_CHECKOUT: {"outcome": CHECKOUT_OUTCOME},
    M_PAIRED_TTFT: {
        "provider": PROVIDER,
        "transport": TRANSPORT,
        "state": frozenset({"cold", "hot"}),
        "le": _le_labels_for(M_PAIRED_TTFT),
    },
    M_RELAY_TTFT: {"provider": PROVIDER, "le": _le_labels_for(M_RELAY_TTFT)},
    M_RELAY_TTFT_FIRST: {
        "provider": PROVIDER,
        "le": _le_labels_for(M_RELAY_TTFT_FIRST),
    },
    M_RELAY_THROUGHPUT: {
        "provider": PROVIDER,
        "le": _le_labels_for(M_RELAY_THROUGHPUT),
    },
    M_RELAY_VRAM_RETRY: {
        "provider": PROVIDER,
        "trigger": frozenset({"initial", "midstream", "silent_eof", "non_streaming"}),
    },
    M_RELAY_WATCHDOG_FIRE: {
        "phase": frozenset({"pre_first_token", "post_first_token"})
    },
    M_RELAY_TRANSPORT: {"transport": TRANSPORT},
    M_TUNNEL_RECONNECT: {
        "cause": frozenset(
            {
                "half_open_stale",
                "ping_fail",
                "read_error",
                "lease_conflict",
                "auth_fail",
                "other",
            }
        )
    },
    M_TUNNEL_BACKOFF_DEPTH: {"le": _le_labels_for(M_TUNNEL_BACKOFF_DEPTH)},
    M_TUNNEL_HEARTBEAT_STALE_CLOSE: {},
    M_MODEL_PULL: {
        "provider": PROVIDER,
        "outcome": frozenset({"success", "error", "cancelled"}),
    },
    M_PROVIDER_AUTO_REVIVE: {"provider": PROVIDER, "outcome": SUCCESS_ERROR},
    M_PROVIDER_OPTIMIZE: {
        "provider": PROVIDER,
        "outcome": frozenset({"success", "error"}),
    },
    M_CTX_HALVE_NUMCTX: {"provider": PROVIDER},
    M_DAEMON_ACTIVE: {"tier": TIER, "kv_halved": BOOL},
    M_CRYPTO_E2EE_HANDSHAKE: {"transport": TRANSPORT, "outcome": SUCCESS_ERROR},
    M_BRIDGE_REQUEST: {
        "provider": PROVIDER,
        "transport": BRIDGE_TRANSPORT,
        "outcome": BRIDGE_OUTCOME,
    },
    M_BRIDGE_TTFT: {
        "transport": BRIDGE_TRANSPORT,
        "le": _le_labels_for(M_BRIDGE_TTFT),
    },
    M_PAIRED_HOST_TTFT: {
        "provider": PROVIDER,
        "transport": TRANSPORT,
        "state": frozenset({"cold", "hot"}),
        "le": _le_labels_for(M_PAIRED_HOST_TTFT),
    },
    M_CTX_FORMULA_FIT: {
        "provider": PROVIDER,
        "family": LOCAL_MODEL_FAMILY,
        "size": MODEL_SIZE_BUCKET,
        "le": _le_labels_for(M_CTX_FORMULA_FIT),
    },
    M_CTX_HW_FIT: {
        "gpu_vendor": GPU_VENDOR,
        "tier": TIER,
        "le": _le_labels_for(M_CTX_HW_FIT),
    },
    M_CTX_CLAMP: {
        "provider": PROVIDER,
        "gpu_vendor": GPU_VENDOR,
        "tier": TIER,
    },
    M_CTX_PREFILL_SPEED: {
        "provider": PROVIDER,
        "tier": TIER,
        "le": _le_labels_for(M_CTX_PREFILL_SPEED),
    },
}

BACKEND_OPS_METRICS = frozenset(
    {
        M_WS_CONNECT,
        M_RELAY_EVENT,
        M_TUNNEL_EVENT,
        M_CHAT_CLASSIFY_DECISION,
        M_CHAT_TOOL_EXECUTION,
        M_CHAT_TOOL_LATENCY,
        M_SEARCH_DIGEST,
        M_SEARCH_ALIAS,
        M_OPENROUTER_CACHE,
        M_CHAT_TTFT,
        M_CHAT_TTFT_FIRST,
        M_CHAT_PEEK_HANDOFF_OVERTURN,
        M_CHAT_REACT_FALLBACK,
        M_CHAT_CONTEXT_OVERFLOW_RETRY,
        M_INFRA_DB_POOL_WAIT,
        M_INFRA_S3_OP,
        M_INFRA_PUSH,
        M_INFRA_RATE_LIMIT_REJECT,
        M_INFRA_RATE_LIMIT_FALLBACK,
        M_INFRA_EXA_QUOTA_BREACH,
        M_AUTH_OTP,
        M_AUTH_GOOGLE,
        M_AUTH_TOKEN_REFRESH,
        M_META_REPORTS_RECEIVED,
        M_PAIR_FINALIZE,
        M_ABUSE_ENFORCEMENT,
        M_CHAT_CLOUD_MODEL,
        M_INFRA_HTTP_5XX,
        M_BILLING_WEBHOOK,
        M_BILLING_CREDIT_SETTLE,
        M_CHAT_PROVIDER_ERROR,
        M_CHAT_STREAM_TERMINAL,
        M_TTS_UNIT,
        M_TTS_PROVIDER,
        M_TTS_COST_MICROUSD,
    }
)

_SHARED_DEVICE_METRICS = frozenset(
    {M_PEEK_OUTCOME, M_PEEK_GUARD_OVERTURN, M_LOOP_GUARD_TRIP}
)

FLUTTER_REPORTABLE_METRICS = (
    frozenset(
        {
            M_CHAT_SECURITY_MODE,
            M_CHAT_ROUTE,
            M_CHAT_TRANSPORT_RESOLUTION,
            M_PEEK_CUTOFF_HANDOFF,
            M_CTX_TRUNCATION,
            M_CTX_HISTORY_EVICTION,
            M_DEVICE_VRAM_DETECTION,
            M_DEVICE_VRAM_TIER,
            M_LOCAL_TTFT,
            M_LOCAL_TTFT_FIRST,
            M_LOCAL_OOM_RETRY,
            M_NET_SERVICE_RECONNECT,
            M_CHAT_TURN_OUTCOME,
            M_CHAT_IMAGE_GENERATION,
            M_CHAT_IMAGE_INPUT,
            M_ONBOARDING_MK_TRANSFER,
            M_LOCAL_THROUGHPUT,
            M_SYNC_OPERATION,
            M_APP_CRASH,
            M_PAIRED_TTFT,
            M_ONBOARDING_STEP,
            M_BILLING_CHECKOUT,
            M_APP_UPDATE,
            M_DAEMON_DEPLOY,
            M_LOCAL_SETUP,
        }
    )
    | _SHARED_DEVICE_METRICS
    | {M_MODEL_PULL}
)

DAEMON_REPORTABLE_METRICS = (
    frozenset(
        {
            M_RELAY_TTFT,
            M_RELAY_TTFT_FIRST,
            M_RELAY_THROUGHPUT,
            M_RELAY_VRAM_RETRY,
            M_RELAY_WATCHDOG_FIRE,
            M_RELAY_TRANSPORT,
            M_TUNNEL_RECONNECT,
            M_TUNNEL_BACKOFF_DEPTH,
            M_TUNNEL_HEARTBEAT_STALE_CLOSE,
            M_MODEL_PULL,
            M_PROVIDER_AUTO_REVIVE,
            M_PROVIDER_OPTIMIZE,
            M_CTX_HALVE_NUMCTX,
            M_DAEMON_ACTIVE,
            M_CRYPTO_E2EE_HANDSHAKE,
            M_BRIDGE_REQUEST,
            M_BRIDGE_TTFT,
            M_PAIRED_HOST_TTFT,
            M_CTX_FORMULA_FIT,
            M_CTX_HW_FIT,
            M_CTX_CLAMP,
            M_CTX_PREFILL_SPEED,
        }
    )
    | _SHARED_DEVICE_METRICS
)

DEVICE_BEHAVIOR_METRICS = FLUTTER_REPORTABLE_METRICS | DAEMON_REPORTABLE_METRICS
ALLOWED_METRICS = BACKEND_OPS_METRICS | DEVICE_BEHAVIOR_METRICS

MAX_DIMS_JSON_BYTES = 512

def serialize_dims(dims: dict | None) -> str:
    """Canonical dims serialization — the byte-for-byte cross-codebase contract.

    Rules: drop None/empty values; stringify every value; sort keys; compact
    separators; ASCII-escape. Empty/None dims serialize to "" (which matches
    the metric_rollup.dims_json server_default).
    """
    if not dims:
        return ""
    clean: dict[str, str] = {}
    for key, value in dims.items():
        if value is None:
            continue
        sval = str(value)
        if sval == "":
            continue
        clean[str(key)] = sval
    if not clean:
        return ""
    return json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def coarsen_version(raw: str | None) -> str:
    """Best-effort coarsen any version string to `major.minor`.

    "1.2.3+build" -> "1.2"; unparseable -> "". Coarsening is mandatory: a full
    semver with build metadata is privacy-sensitive (near-unique per build) and
    is rejected/collapsed here.
    """
    if not raw:
        return ""
    match = re.match(r"^\s*(\d{1,4})\.(\d{1,4})", str(raw))
    if not match:
        return ""
    return f"{match.group(1)}.{match.group(2)}"


def cloud_model_family(model_id: str | None) -> str:
    """Map an OpenRouter model id to its coarse, bounded MODEL_FAMILY value
    for the chat.cloud_model metric. Never returns an exact id — anything
    unrecognised collapses to 'other'. Pure substring match on the lowered id.
    """
    m = (model_id or "").lower()
    if not m:
        return "other"
    if "gpt-oss" in m or "gpt_oss" in m:
        return "gpt_oss"
    if "kimi" in m or "moonshot" in m:
        return "kimi"
    if "minimax" in m:
        return "minimax"
    if "deepseek" in m:
        return "deepseek"
    if "glm" in m:
        return "glm"
    if "gemma" in m:
        return "gemma"
    if "qwen" in m:
        return "qwen"
    if "llama" in m:
        return "llama"
    if "mistral" in m or "mixtral" in m or "ministral" in m:
        return "mistral"
    if "stepfun" in m:
        return "step"
    return "other"


_ROUTE_GROUP_PREFIXES: tuple[tuple[str, str], ...] = (
    ("/v1/auth", "auth"),
    ("/v1/chat", "chat"),
    ("/v1/sync", "sync"),
    ("/v1/billing", "billing"),
    ("/v1/pairing", "pairing"),
    ("/v1/models", "models"),
    ("/v1/p2p", "p2p"),
    ("/v1/metrics", "metrics"),
    ("/webhooks", "webhooks"),
    ("/ops", "ops"),
)


def http_route_group(path: str | None) -> str:
    """Map a request path to its bounded ROUTE_GROUP value ('other' fallback).

    Never returns the raw path — the dim must stay a bounded enum.
    """
    p = str(path or "")
    for prefix, group in _ROUTE_GROUP_PREFIXES:
        if p.startswith(prefix):
            return group
    return "other"


def histogram_le(value: float, metric: str) -> str:
    """Map a numeric observation to its `le` bucket label for `metric`."""
    bounds = METRIC_BUCKETS.get(metric)
    if bounds is None:
        raise ValueError(f"{metric} is not a histogram metric")
    for bound in bounds:
        if value <= bound:
            return str(bound)
    return "inf"


def is_reportable(metric: str, source: str) -> bool:
    """True if a reporter of `source` ('flutter'|'daemon') may report `metric`."""
    if source == "flutter":
        return metric in FLUTTER_REPORTABLE_METRICS
    if source == "daemon":
        return metric in DAEMON_REPORTABLE_METRICS
    return False


def clean_dims_for_metric(metric: str, raw_dims: dict | None) -> dict[str, str]:
    """Validate + clean client-provided dims against METRIC_DIM_SPEC.

    Returns the cleaned {str: str} dims. Raises ValueError if the metric is
    unknown, a dim key is not allowed for the metric, or a value is outside the
    bounded vocabulary. This is the privacy allowlist gate for ingestion.
    """
    spec = METRIC_DIM_SPEC.get(metric)
    if spec is None:
        raise ValueError(f"unknown metric: {metric}")
    out: dict[str, str] = {}
    for key, value in (raw_dims or {}).items():
        skey = str(key)
        allowed = spec.get(skey)
        if allowed is None:
            raise ValueError(f"dim '{skey}' not allowed for {metric}")
        sval = str(value)
        if sval not in allowed:
            raise ValueError(f"dim '{skey}'='{sval}' outside vocab for {metric}")
        out[skey] = sval
    return out


def _self_check() -> None:
    for metric in ALLOWED_METRICS:
        if ":" in metric:
            raise AssertionError(f"metric name contains ':' — {metric}")
        if metric not in METRIC_DIM_SPEC:
            raise AssertionError(f"metric missing from METRIC_DIM_SPEC — {metric}")
    for metric in METRIC_DIM_SPEC:
        if metric not in ALLOWED_METRICS:
            raise AssertionError(f"METRIC_DIM_SPEC has unknown metric — {metric}")
    for metric in METRIC_BUCKETS:
        le_vocab = METRIC_DIM_SPEC[metric].get("le")
        if le_vocab != _le_labels_for(metric):
            raise AssertionError(f"le vocab mismatch for histogram metric — {metric}")


_self_check()
