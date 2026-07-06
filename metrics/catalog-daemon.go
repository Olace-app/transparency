// Package metrics is the daemon's aggregate, identifier-free metrics layer.
//
// LOCKSTEP CONTRACT
// =================
// The metric names, dimension keys, dimension values, and histogram bucket
// labels below are mirrored byte-for-byte in:
//   - Backend — Backend/utils/infra/metrics_catalog.py
//   - Flutter — Flutter/lib/constants/metric_constants.dart
//
// Any edit here REQUIRES a matching edit in both. The backend aggregates
// rolled-up counters by exact string equality; a single drifted string
// ("need_tool" vs "needs_tool", "1000" vs "1000.0") silently splits one
// logical counter into two with no error anywhere.
//
// PRIVACY: every dimension value here is a bounded enum. No dimension ever
// carries an identifier (device id, pair id, IP, model name) or user content.
// This package is a leaf — it must not import internal/tunnel, internal/
// inference, or internal/config (that would create an import cycle).
package metrics

import (
	"strconv"
	"time"
)

// Metric names — daemon-emitted device-behavior tier (mirrors the Python
// DAEMON_REPORTABLE_METRICS set). Dotted, colon-free.
const (
	MetricPeekOutcome               = "peek.outcome"
	MetricPeekGuardOverturn         = "peek.guard_overturn"
	MetricRelayTTFT                 = "relay.ttft"
	MetricRelayTTFTFirst            = "relay.ttft_first"
	MetricRelayThroughput           = "relay.throughput"
	MetricRelayVRAMRetry            = "relay.vram_retry"
	MetricRelayWatchdogFire         = "relay.watchdog_fire"
	MetricRelayTransport            = "relay.transport"
	MetricTunnelReconnect           = "tunnel.reconnect"
	MetricTunnelBackoffDepth        = "tunnel.backoff_depth"
	MetricTunnelHeartbeatStaleClose = "tunnel.heartbeat_stale_close"
	MetricModelPull                 = "model.pull"
	MetricProviderAutoRevive        = "provider.auto_revive"
	MetricProviderOptimize          = "provider.optimize"
	MetricCtxHalveNumCtx            = "ctx.halve_numctx"
	MetricDaemonActive              = "daemon.active"
	MetricCryptoE2EEHandshake       = "crypto.e2ee_handshake"
	MetricDeviceVRAMDetection       = "device.vram_detection" // Flutter-only; mirrored for catalog lockstep.
	MetricBridgeRequest             = "bridge.request"
	MetricBridgeTTFT                = "bridge.ttft"
)

// Dimension keys.
const (
	DimVariant   = "variant"
	DimDecision  = "decision"
	DimProvider  = "provider"
	DimLE        = "le"
	DimTrigger   = "trigger"
	DimPhase     = "phase"
	DimTransport = "transport"
	DimCause     = "cause"
	DimOutcome   = "outcome"
	DimTier      = "tier"
	DimKVHalved  = "kv_halved"
	DimSource    = "source"
)

// Dimension values (bounded enums).
const (
	VariantDaemon = "daemon"

	// peek.Decision.String() values — byte-identical to the daemon enum so a
	// call site may pass decision.String() straight through.
	DecisionDirectAnswer  = "direct_answer"
	DecisionNeedTool      = "need_tool"
	DecisionToolDirective = "tool_directive"
	DecisionCutoff        = "cutoff"
	DecisionError         = "error"

	ProviderOllama   = "ollama"
	ProviderLMStudio = "lmstudio"

	TriggerInitial      = "initial"
	TriggerMidstream    = "midstream"
	TriggerSilentEOF    = "silent_eof"
	TriggerNonStreaming = "non_streaming"

	PhasePreFirstToken  = "pre_first_token"
	PhasePostFirstToken = "post_first_token"

	TransportLANP2P = "lan_p2p"
	TransportRelay  = "relay"

	CauseHalfOpenStale = "half_open_stale"
	CausePingFail      = "ping_fail"
	CauseReadError     = "read_error"
	CauseLeaseConflict = "lease_conflict"
	CauseAuthFail      = "auth_fail"
	CauseOther         = "other"

	OutcomeSuccess   = "success"
	OutcomeError     = "error"
	OutcomeCancelled = "cancelled"

	SourceDaemon          = "daemon"
	SourceFlutterFallback = "flutter_fallback"
	SourceUnknown         = "unknown"

	// bridge.request transport values (TransportLANP2P/TransportRelay
	// above plus the bridge-only local value) and outcome values.
	TransportLocal = "local"

	BridgeOutcomeSuccess       = "success"
	BridgeOutcomeCancelled     = "cancelled"
	BridgeOutcomeInvalid       = "invalid_request"
	BridgeOutcomeUnauthorized  = "unauthorized"
	BridgeOutcomeNotFound      = "not_found"
	BridgeOutcomeForbidden     = "forbidden"
	BridgeOutcomeRateLimited   = "rate_limited"
	BridgeOutcomeHostOffline   = "host_offline"
	BridgeOutcomeTimeout       = "timeout"
	BridgeOutcomeProviderError = "provider_error"
	BridgeOutcomeInternal      = "internal"
)

// Histogram bucket bounds. A histogram is a plain counter with an extra `le`
// dimension; each observation lands in exactly one bucket (non-cumulative).
// The label "inf" is the overflow bucket. These bound sets MUST match the
// Python LE_*_BOUNDS and the Flutter MetricBuckets.
var (
	leLatencyBoundsMS     = []int64{200, 500, 1000, 2000, 5000, 10000}
	leThroughputBoundsTPS = []float64{5, 10, 20, 40, 80}
	leBackoffBoundsMS     = []int64{2000, 5000, 10000, 20000}
)

// BucketLE maps a latency observation (ms) to its `le` bucket label.
func BucketLE(ms int64) string {
	for _, b := range leLatencyBoundsMS {
		if ms <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

// BucketThroughput maps a throughput observation (tokens/sec) to its label.
func BucketThroughput(tps float64) string {
	for _, b := range leThroughputBoundsTPS {
		if tps <= b {
			return strconv.FormatFloat(b, 'f', -1, 64)
		}
	}
	return "inf"
}

// BucketBackoff maps a reconnect backoff observation (ms) to its label.
func BucketBackoff(ms int64) string {
	for _, b := range leBackoffBoundsMS {
		if ms <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

// BoolStr renders a bool as the canonical "true"/"false" dimension value.
func BoolStr(v bool) string {
	if v {
		return "true"
	}
	return "false"
}

// RecordBridgeRequest records one bridge.request observation. provider ∈
// {ollama, lmstudio}; transport ∈ {local, lan_p2p, relay}; outcome is one
// of the BridgeOutcome* enums. No identifiers, no model names.
func RecordBridgeRequest(col *Collector, provider, transport, outcome string) {
	if col == nil {
		return
	}
	col.Incr(MetricBridgeRequest, map[string]string{
		DimProvider:  provider,
		DimTransport: transport,
		DimOutcome:   outcome,
	}, 1)
}

// RecordBridgeTTFT records one bridge.ttft histogram observation.
func RecordBridgeTTFT(col *Collector, transport string, d time.Duration) {
	if col == nil {
		return
	}
	col.Observe(MetricBridgeTTFT, map[string]string{
		DimTransport: transport,
	}, d.Milliseconds())
}

// RecordE2EEHandshake records one crypto.e2ee_handshake observation —
// transport is TransportRelay or TransportLANP2P; ok is the handshake
// result. col may be nil (metrics not yet wired) — then it is a no-op.
func RecordE2EEHandshake(col *Collector, transport string, ok bool) {
	if col == nil {
		return
	}
	outcome := OutcomeError
	if ok {
		outcome = OutcomeSuccess
	}
	col.Incr(MetricCryptoE2EEHandshake, map[string]string{
		DimTransport: transport,
		DimOutcome:   outcome,
	}, 1)
}
