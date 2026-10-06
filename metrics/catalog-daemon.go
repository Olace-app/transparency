package metrics

import (
	"strconv"
	"strings"
	"time"
)

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
	MetricDeviceVRAMDetection       = "device.vram_detection"
	MetricBridgeRequest             = "bridge.request"
	MetricBridgeTTFT                = "bridge.ttft"
	MetricPairedTTFT                = "paired.ttft"
	MetricPairedHostTTFT            = "paired.host_ttft"
	MetricCtxFormulaFit             = "ctx.formula_fit"
	MetricCtxHwFit                  = "ctx.hw_fit"
	MetricCtxClamp                  = "ctx.clamp"
	MetricCtxPrefillSpeed           = "ctx.prefill_speed"
	MetricLoopGuardTrip             = "local.loop_guard_trip"
)

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
	DimState     = "state"
	DimStream    = "stream"
	DimFamily    = "family"
	DimSize      = "size"
	DimGPUVendor = "gpu_vendor"
)

const (
	VariantDaemon = "daemon"

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

	StateCold = "cold"
	StateHot  = "hot"

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

	LoopStreamVisible = "visible"
	LoopStreamThought = "thought"

	LoopTierShort  = "short"
	LoopTierBlock  = "block"
	LoopTierBudget = "budget"
)

var (
	leLatencyBoundsMS     = []int64{200, 500, 1000, 2000, 5000, 10000}
	leThroughputBoundsTPS = []float64{5, 10, 20, 40, 80}
	leBackoffBoundsMS     = []int64{2000, 5000, 10000, 20000}
	leRatioBoundsPct      = []int64{40, 60, 80, 95, 110, 130, 160, 200, 300, 500}
	lePrefillBoundsTPS    = []int64{50, 150, 400, 1000, 3000}
)

func BucketLE(ms int64) string {
	for _, b := range leLatencyBoundsMS {
		if ms <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

func BucketThroughput(tps float64) string {
	for _, b := range leThroughputBoundsTPS {
		if tps <= b {
			return strconv.FormatFloat(b, 'f', -1, 64)
		}
	}
	return "inf"
}

func BucketBackoff(ms int64) string {
	for _, b := range leBackoffBoundsMS {
		if ms <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

func BoolStr(v bool) string {
	if v {
		return "true"
	}
	return "false"
}

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

func RecordBridgeTTFT(col *Collector, transport string, d time.Duration) {
	if col == nil {
		return
	}
	col.Observe(MetricBridgeTTFT, map[string]string{
		DimTransport: transport,
	}, d.Milliseconds())
}

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

func BucketRatioPct(pct int64) string {
	for _, b := range leRatioBoundsPct {
		if pct <= b {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

func BucketPrefillTPS(tps float64) string {
	for _, b := range lePrefillBoundsTPS {
		if tps <= float64(b) {
			return strconv.FormatInt(b, 10)
		}
	}
	return "inf"
}

func LocalModelFamily(modelID string) string {
	id := strings.ToLower(modelID)
	for _, fam := range []string{"llama", "qwen", "gemma", "deepseek", "mistral", "phi"} {
		if strings.Contains(id, fam) {
			return fam
		}
	}
	return "other"
}

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
