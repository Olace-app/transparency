library;

class MetricNames {
  MetricNames._();

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
  static const String modelPull = 'model.pull';

  static const String loopGuardTrip = 'local.loop_guard_trip';

  static const String appCrash = 'app.crash';

  static const String pairedTtft = 'paired.ttft';

  static const String onboardingStep = 'onboarding.step';
  static const String appUpdate = 'app.update';
  static const String daemonDeploy = 'daemon.deploy';
  static const String localSetup = 'local.setup';
  static const String billingCheckout = 'billing.checkout';

  static const String bridgeRequest = 'bridge.request';
  static const String bridgeTtft = 'bridge.ttft';
  static const String pairedHostTtft = 'paired.host_ttft';
}

class MetricDims {
  MetricDims._();

  static const String mode = 'mode';
  static const String route = 'route';
  static const String transport = 'transport';
  static const String provider = 'provider';
  static const String cloudKey = 'cloud_key';
  static const String errorKind = 'error_kind';
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
  static const String reason = 'reason';
  static const String fault = 'fault';
  static const String surface = 'surface';

  static const String stream = 'stream';

  static const String step = 'step';
  static const String event = 'event';
  static const String trigger = 'trigger';
}

class MetricValues {
  MetricValues._();

  static const String securityStandard = 'standard';
  static const String securityMaxPrivacy = 'max_privacy';

  static const String routeLocal = 'local';
  static const String routePaired = 'paired';
  static const String routeCloud = 'cloud';

  static const String transportLanP2p = 'lan_p2p';
  static const String transportRelay = 'relay';
  static const String transportLocal = 'local';

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

  static const String providerOllama = 'ollama';
  static const String providerLmStudio = 'lmstudio';
  static const String providerLlamacpp = 'llamacpp';

  static const String cloudOlace = 'olace';
  static const String cloudByok = 'byok';

  static const String loopStreamVisible = 'visible';
  static const String loopStreamThought = 'thought';
  static const String loopTierShort = 'short';
  static const String loopTierBlock = 'block';
  static const String loopTierBudget = 'budget';

  static const String variantLargeLocal = 'large_local';
  static const String variantSmallLocal = 'small_local';
  static const String variantPairedLan = 'paired_lan';
  static const String variantPairedRelay = 'paired_relay';

  static const String decisionDirectAnswer = 'direct_answer';
  static const String decisionNeedTool = 'need_tool';
  static const String decisionToolDirective = 'tool_directive';
  static const String decisionCutoff = 'cutoff';
  static const String decisionError = 'error';

  static const String blockOtherFiles = 'other_files';
  static const String blockResearchFiles = 'research_files';
  static const String blockAttachedFiles = 'attached_files';
  static const String blockProjectFiles = 'project_files';
  static const String blockAttachments = 'attachments';

  static const String stateCold = 'cold';
  static const String stateHot = 'hot';

  static const String reasonHot = 'hot';
  static const String reasonPingOk = 'ping_ok';
  static const String reasonProbeOk = 'probe_ok';
  static const String reasonHomeKnown = 'home_known';
  static const String reasonWeb = 'web';
  static const String reasonSubwindow = 'subwindow';
  static const String reasonLanUnavailable = 'lan_unavailable';
  static const String reasonHandshakeBlocked = 'handshake_blocked';
  static const String reasonRecentlyUnreachable = 'recently_unreachable';
  static const String reasonNetworkChanged = 'network_changed';
  static const String reasonPingFailed = 'ping_failed';
  static const String reasonProbeUnproven = 'probe_unproven';
  static const String reasonProbeTimeout = 'probe_timeout';
  static const String reasonProbeError = 'probe_error';
  static const String reasonLanNotPreferred = 'lan_not_preferred';

  static const String serviceChatSocket = 'chat_socket';
  static const String serviceDeviceRealtime = 'device_realtime';
  static const String serviceDesktopTunnel = 'desktop_tunnel';

  static const String lifecycleForeground = 'foreground';
  static const String lifecycleBackground = 'background';

  static const String sourceDaemon = 'daemon';
  static const String sourceFlutterFallback = 'flutter_fallback';
  static const String sourceUnknown = 'unknown';

  static const String outcomeCompleted = 'completed';
  static const String outcomeError = 'error';
  static const String outcomeCancelled = 'cancelled';
  static const String outcomeSuccess = 'success';

  static const String boolTrue = 'true';
  static const String boolFalse = 'false';
  static const String faultWidget = 'widget';
  static const String faultAsync = 'async';

  static const String surfaceLeader = 'leader';
  static const String surfaceSubwindow = 'subwindow';

  static const String stepSignIn = 'sign_in';
  static const String stepTrial = 'trial';
  static const String stepSync = 'sync';
  static const String stepPair = 'pair';
  static const String stepDone = 'done';

  static const String eventShown = 'shown';
  static const String eventCompleted = 'completed';
  static const String eventSkipped = 'skipped';
  static const String eventResumed = 'resumed';

  static const String checkoutOpened = 'opened';
  static const String checkoutLaunched = 'launched';
  static const String checkoutCompleted = 'completed';
  static const String checkoutPending = 'pending';
  static const String checkoutCancelled = 'cancelled';
  static const String checkoutFailed = 'failed';
  static const String checkoutElsewhere = 'elsewhere';
}

class MetricBuckets {
  MetricBuckets._();

  static const List<int> latencyBoundsMs = [200, 500, 1000, 2000, 5000, 10000];

  static String latencyLe(int valueMs) {
    for (final bound in latencyBoundsMs) {
      if (valueMs <= bound) return bound.toString();
    }
    return 'inf';
  }

  static const List<int> throughputBoundsTps = [5, 10, 20, 40, 80];

  static String throughputLe(num valueTps) {
    for (final bound in throughputBoundsTps) {
      if (valueTps <= bound) return bound.toString();
    }
    return 'inf';
  }

  static String boolValue(bool value) =>
      value ? MetricValues.boolTrue : MetricValues.boolFalse;
}
