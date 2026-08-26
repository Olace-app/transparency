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
	"strings"
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
	MetricProviderAutoRevive        = "provider.auto_revive" // dims: provider + outcome (success/error)
	MetricProviderOptimize          = "provider.optimize"
	MetricCtxHalveNumCtx            = "ctx.halve_numctx"
	MetricDaemonActive              = "daemon.active"
	MetricCryptoE2EEHandshake       = "crypto.e2ee_handshake"
	MetricDeviceVRAMDetection       = "device.vram_detection" // Flutter-only; mirrored for catalog lockstep.
	MetricBridgeRequest             = "bridge.request"
	MetricBridgeTTFT                = "bridge.ttft"
	// paired.host_ttft is the HOST half of a paired turn: peek request
	// received -> first answer token handed to the carrier. Its consumer-side
	// twin, paired.ttft, is emitted by the Flutter consumer over the same
	// turn. Neither is derivable from the other (different reporters, different
	// platform dim), and the gap between their medians IS the carrier tax —
	// which is the whole reason both exist. paired.ttft is Flutter-only and
	// mirrored below purely for catalog lockstep, same as device.vram_detection.
	MetricPairedTTFT     = "paired.ttft"
	MetricPairedHostTTFT = "paired.host_ttft"
	// Fleet calibration fit — how far the ctx-budget formula's prediction
	// sits from what this machine actually verified, as an integer-percent
	// ratio histogram (100 = formula exact, 60 = verified 60% of the
	// prediction). TWO MARGINAL views by design: formula_fit slices by
	// model family + size bucket (the axes the budget constants are keyed
	// on), hw_fit by gpu vendor + tier. The joint (rare GPU x rare model)
	// cell would be one identifiable machine, so it is never formed.
	// Never an exact model id — family + download-size bucket only.
	MetricCtxFormulaFit = "ctx.formula_fit"
	MetricCtxHwFit      = "ctx.hw_fit"
	// One 3-strike calibration clamp landed: the formula over-predicted on
	// this hardware class badly enough for three real OOMs.
	MetricCtxClamp = "ctx.clamp"
	// Cold prefill speed (prompt tokens/sec) per hardware tier. Full
	// prefills only — KV-warm turns are suppressed at the emit site, since
	// their near-zero prefill would poison the histogram.
	MetricCtxPrefillSpeed = "ctx.prefill_speed"
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
	// DimState splits a TTFT observation by whether the model had to be
	// loaded first. Mirrors the Flutter `state` dim on local.ttft.
	DimState = "state"
	// ctx.formula_fit / ctx.hw_fit / ctx.clamp dims.
	DimFamily    = "family"
	DimSize      = "size"
	DimGPUVendor = "gpu_vendor"
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
	ProviderLlamaCpp = "llamacpp"

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

	// paired.host_ttft / local.ttft `state` values — StateCold means a model
	// load or runtime wake ran before the first token, so the observation
	// measures a load rather than the model's responsiveness.
	StateCold = "cold"
	StateHot  = "hot"

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
	// Integer arrays on purpose: FormatInt labels cannot drift from the
	// Python str(int) / Dart int.toString() forms the way float bounds can.
	leRatioBoundsPct   = []int64{40, 60, 80, 95, 110, 130, 160}
	lePrefillBoundsTPS = []int64{50, 150, 400, 1000, 3000}
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
// {ollama, lmstudio, llamacpp} or "" when unknown (auth/parse rejections
// happen before model resolution — the dim is omitted then, since a missing
// dim is legal server-side but an empty value is out-of-vocab and dropped);
// transport ∈ {local, lan_p2p, relay}; outcome is one of the BridgeOutcome*
// enums. No identifiers, no model names.
func RecordBridgeRequest(col *Collector, provider, transport, outcome string) {
	if col == nil {
		return
	}
	dims := map[string]string{
		DimTransport: transport,
		DimOutcome:   outcome,
	}
	if provider != "" {
		dims[DimProvider] = provider
	}
	col.Incr(MetricBridgeRequest, dims, 1)
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

// RecordPairedHostTTFT records one paired.host_ttft histogram observation —
// the host-side half of a paired turn, measured from peek-request receipt to
// the first answer token handed to the carrier.
//
// provider ∈ {ollama, lmstudio, llamacpp}; transport ∈ {lan_p2p, relay}; cold
// reports whether a model load ran inside the window. A turn whose provider or
// carrier is unknown is dropped rather than reported under an empty dim value
// (out-of-vocab dims are discarded server-side, which would silently split the
// histogram).
func RecordPairedHostTTFT(col *Collector, provider, transport string, cold bool, d time.Duration) {
	if col == nil || provider == "" || transport == "" {
		return
	}
	state := StateHot
	if cold {
		state = StateCold
	}
	col.Observe(MetricPairedHostTTFT, map[string]string{
		DimProvider:  provider,
		DimTransport: transport,
		DimState:     state,
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

// BucketRatioPct maps an integer-percent ratio to its `le` bucket label.
func BucketRatioPct(pct int64) string {
	for _, b := range leRatioBoundsPct {
		if pct <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

// BucketPrefillTPS maps a prefill speed (prompt tokens/sec) to its label.
func BucketPrefillTPS(tps float64) string {
	for _, b := range lePrefillBoundsTPS {
		if tps <= float64(b) {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

// LocalModelFamily maps a local model tag to the coarse family vocabulary
// mirrored in the backend LOCAL_MODEL_FAMILY set. Substring match, same
// rule as the backend's cloud_model_family: never the exact tag — a
// hand-pulled hf.co repo name is user-chosen text and collapses to
// "other" like everything unrecognised.
func LocalModelFamily(modelID string) string {
	id := strings.ToLower(modelID)
	for _, fam := range []string{"llama", "qwen", "gemma", "deepseek", "mistral", "phi"} {
		if strings.Contains(id, fam) {
			return fam
		}
	}
	return "other"
}

// ModelSizeBucket maps an on-disk download size (GB) to the bucket
// vocabulary mirrored in the backend MODEL_SIZE_BUCKET set.
func ModelSizeBucket(downloadGB float64) string {
	switch {
	case downloadGB < 2:
		return "lt2"
	case downloadGB < 4:
		return "2_4"
	case downloadGB < 8:
		return "4_8"
	default:
		return "8plus"
	}
}

// GPUVendorClass maps a detected GPU vendor to the bounded vocabulary
// mirrored in the backend GPU_VENDOR set. "other" covers no-GPU hosts and
// anything unrecognised.
func GPUVendorClass(vendor string) string {
	switch strings.ToLower(strings.TrimSpace(vendor)) {
	case "nvidia":
		return "nvidia"
	case "amd":
		return "amd"
	case "apple":
		return "apple"
	case "intel":
		return "intel"
	default:
		return "other"
	}
}

// RecordCtxFit records one verified-calibration observation into BOTH
// marginal fit histograms. ratioPct is round(100 * verified_ctx /
// formula_ctx); provider ∈ {ollama, lmstudio, llamacpp}; modelID and
// downloadGB are coarsened here (family + size bucket — the exact tag
// never leaves this function); vendor and tier describe the hardware
// class. Empty provider or tier drops the observation rather than
// emitting an out-of-vocab dim the server would discard anyway.
func RecordCtxFit(col *Collector, provider, modelID string, downloadGB float64, vendor, tier string, ratioPct int64) {
	if col == nil || provider == "" || tier == "" {
		return
	}
	le := BucketRatioPct(ratioPct)
	col.Incr(MetricCtxFormulaFit, map[string]string{
		DimProvider: provider,
		DimFamily:   LocalModelFamily(modelID),
		DimSize:     ModelSizeBucket(downloadGB),
		DimLE:       le,
	}, 1)
	col.Incr(MetricCtxHwFit, map[string]string{
		DimGPUVendor: GPUVendorClass(vendor),
		DimTier:      tier,
		DimLE:        le,
	}, 1)
}

// RecordCtxClamp records one landed 3-strike calibration clamp.
func RecordCtxClamp(col *Collector, provider, vendor, tier string) {
	if col == nil || provider == "" || tier == "" {
		return
	}
	col.Incr(MetricCtxClamp, map[string]string{
		DimProvider:  provider,
		DimGPUVendor: GPUVendorClass(vendor),
		DimTier:      tier,
	}, 1)
}

// RecordCtxPrefillSpeed records one cold-prefill speed observation. The
// caller is responsible for suppressing KV-warm turns (near-zero prompt
// eval) — see the MetricCtxPrefillSpeed comment.
func RecordCtxPrefillSpeed(col *Collector, provider, tier string, tps float64) {
	if col == nil || provider == "" || tier == "" || tps <= 0 {
		return
	}
	col.Incr(MetricCtxPrefillSpeed, map[string]string{
		DimProvider: provider,
		DimTier:     tier,
		DimLE:       BucketPrefillTPS(tps),
	}, 1)
}
