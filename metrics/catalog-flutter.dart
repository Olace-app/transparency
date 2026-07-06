/// Metric catalog constants — the Flutter side of the cross-codebase
/// metrics lockstep contract.
///
/// LOCKSTEP: every metric name, dimension key, dimension value, and `le`
/// histogram bucket label below is mirrored byte-for-byte in:
///   * Backend — Backend/utils/infra/metrics_catalog.py
///   * Daemon  — Daemon/internal/metrics/catalog.go
/// Any edit here REQUIRES a matching edit in both. The backend aggregates
/// rolled-up counters by exact string equality; a single drifted string
/// silently splits one logical counter into two with no error anywhere.
///
/// PRIVACY: every dimension value here is a bounded enum. A metric never
/// carries an identifier (device id, conversation id, IP) or user content.
/// `maximum_privacy_v1` (Direct Mode) conversations may only ever emit
/// [MetricNames.chatSecurityMode] — nothing else.
library;

/// Metric names emitted by the Flutter client (the device-behavior tier).
class MetricNames {
  MetricNames._();

  /// The ONLY metric permitted for a Direct Mode conversation.
  static const String chatSecurityMode = 'chat.security_mode';
  static const String chatRoute = 'chat.route';
  static const String chatTransportResolution = 'chat.transport_resolution';
  static const String peekOutcome = 'peek.outcome';
  static const String peekGuardOverturn = 'peek.guard_overturn';
  static const String peekCutoffHandoff = 'peek.cutoff_handoff';
  static const String ctxTruncation = 'ctx.truncation';
  static const String ctxHistoryEviction = 'ctx.history_eviction';
  static const String deviceVramDetection = 'device.vram_detection';
  static const String deviceVramTier = 'device.vram_tier';
  static const String localTtft = 'local.ttft';
  static const String localTtftFirst = 'local.ttft_first';
  static const String localOomRetry = 'local.oom_retry';
  static const String netServiceReconnect = 'net.service_reconnect';
  static const String chatTurnOutcome = 'chat.turn_outcome';
  static const String chatImageGeneration = 'chat.image_generation';
  static const String chatImageInput = 'chat.image_input';
  static const String onboardingMkTransfer = 'onboarding.mk_transfer';
  static const String localThroughput = 'local.throughput';
  static const String syncOperation = 'sync.operation';

  // Olace Bridge (daemon-only emitters; mirrored here for catalog lockstep,
  // same as device.vram_detection is mirrored in the Go catalog).
  static const String bridgeRequest = 'bridge.request';
  static const String bridgeTtft = 'bridge.ttft';
}

/// Dimension keys.
class MetricDims {
  MetricDims._();

  static const String mode = 'mode';
  static const String route = 'route';
  static const String transport = 'transport';
  static const String provider = 'provider';
  static const String cloudKey = 'cloud_key';
  static const String variant = 'variant';
  static const String decision = 'decision';
  static const String suppressed = 'suppressed';
  static const String blockType = 'block_type';
  static const String tier = 'tier';
  static const String kvHalved = 'kv_halved';
  static const String state = 'state';
  static const String service = 'service';
  static const String lifecycle = 'lifecycle';
  static const String source = 'source';
  static const String le = 'le';
  static const String outcome = 'outcome';
}

/// Bounded dimension values.
class MetricValues {
  MetricValues._();

  // security_mode
  static const String securityStandard = 'standard';
  static const String securityMaxPrivacy = 'max_privacy';

  // route
  static const String routeLocal = 'local';
  static const String routePaired = 'paired';
  static const String routeCloud = 'cloud';

  // transport
  static const String transportLanP2p = 'lan_p2p';
  static const String transportRelay = 'relay';
  // bridge.request / bridge.ttft only — the request was served on the
  // same machine (no paired hop).
  static const String transportLocal = 'local';

  // bridge.request outcome
  static const String bridgeOutcomeSuccess = 'success';
  static const String bridgeOutcomeCancelled = 'cancelled';
  static const String bridgeOutcomeInvalid = 'invalid_request';
  static const String bridgeOutcomeUnauthorized = 'unauthorized';
  static const String bridgeOutcomeNotFound = 'not_found';
  static const String bridgeOutcomeForbidden = 'forbidden';
  static const String bridgeOutcomeRateLimited = 'rate_limited';
  static const String bridgeOutcomeHostOffline = 'host_offline';
  static const String bridgeOutcomeTimeout = 'timeout';
  static const String bridgeOutcomeProviderError = 'provider_error';
  static const String bridgeOutcomeInternal = 'internal';

  // provider
  static const String providerOllama = 'ollama';
  static const String providerLmStudio = 'lmstudio';

  // cloud_key
  static const String cloudOlace = 'olace';
  static const String cloudByok = 'byok';

  // peek variant (Flutter side — the daemon emits variant=daemon)
  static const String variantLargeLocal = 'large_local';
  static const String variantSmallLocal = 'small_local';
  static const String variantPairedLan = 'paired_lan';
  static const String variantPairedRelay = 'paired_relay';

  // peek decision
  static const String decisionDirectAnswer = 'direct_answer';
  static const String decisionNeedTool = 'need_tool';
  static const String decisionToolDirective = 'tool_directive';
  static const String decisionCutoff = 'cutoff';
  static const String decisionError = 'error';

  // ctx truncation block_type
  static const String blockOtherFiles = 'other_files';
  static const String blockResearchFiles = 'research_files';
  static const String blockAttachedFiles = 'attached_files';
  static const String blockProjectFiles = 'project_files';
  static const String blockAttachments = 'attachments';

  // local.ttft state
  static const String stateCold = 'cold';
  static const String stateHot = 'hot';

  // net.service_reconnect service
  static const String serviceChatSocket = 'chat_socket';
  static const String serviceDeviceRealtime = 'device_realtime';
  static const String serviceDesktopTunnel = 'desktop_tunnel';

  // net.service_reconnect lifecycle
  static const String lifecycleForeground = 'foreground';
  static const String lifecycleBackground = 'background';

  // device.vram_detection source
  static const String sourceDaemon = 'daemon';
  static const String sourceFlutterFallback = 'flutter_fallback';
  static const String sourceUnknown = 'unknown';

  // turn / operation outcome — chat.turn_outcome (completed/error/cancelled),
  // chat.image_generation / onboarding.mk_transfer / sync.operation
  // (success/error).
  static const String outcomeCompleted = 'completed';
  static const String outcomeError = 'error';
  static const String outcomeCancelled = 'cancelled';
  static const String outcomeSuccess = 'success';

  // bool dimension value (kv_halved, suppressed)
  static const String boolTrue = 'true';
  static const String boolFalse = 'false';
}

/// Histogram bucketing. A histogram is a plain counter with an extra `le`
/// dimension; each observation lands in exactly one bucket (non-cumulative).
class MetricBuckets {
  MetricBuckets._();

  /// Latency upper bounds (ms) — MUST match Backend LE_LATENCY_BOUNDS_MS and
  /// Daemon leLatencyBoundsMS.
  static const List<int> latencyBoundsMs = [200, 500, 1000, 2000, 5000, 10000];

  /// Maps a latency observation (ms) to its `le` bucket label.
  static String latencyLe(int valueMs) {
    for (final bound in latencyBoundsMs) {
      if (valueMs <= bound) return bound.toString();
    }
    return 'inf';
  }

  /// Throughput upper bounds (tokens/sec) — MUST match Backend
  /// LE_THROUGHPUT_BOUNDS_TPS and Daemon leThroughputBoundsTPS.
  static const List<int> throughputBoundsTps = [5, 10, 20, 40, 80];

  /// Maps a throughput observation (tokens/sec) to its `le` bucket label.
  static String throughputLe(num valueTps) {
    for (final bound in throughputBoundsTps) {
      if (valueTps <= bound) return bound.toString();
    }
    return 'inf';
  }

  /// Canonical "true"/"false" for a bool dimension value.
  static String boolValue(bool value) =>
      value ? MetricValues.boolTrue : MetricValues.boolFalse;
}
