# MCP Positive Deltas + Retrieval Effectiveness Report (Staging)

*Generated 2026-02-24T03:20:10.899060+00:00; integrates the valid-task MCP delta audit with the IR analysis pipeline output.*

## What Was Fixed

- The earlier `MCP_POSITIVE_DELTAS_VALID_RUNS_20260224.*` report was removed because it incorrectly filtered at the **run level**.
- This report uses **task-level validity filtering** (exclude only task pairs affected by rate limiting, Docker/container failures, or infra/setup/API issues).
- MCP direct task IDs with the `sgonly_` prefix are normalized before pairing.

## Scope And Methodology

- Universe: all non-archived/non-broken benchmark runs currently in `runs/staging` with a baseline/MCP config pair.
- MCP delta ranking: task-level reward delta = `MCP reward - baseline reward`, excluding infra-invalid task pairs only.
- IR analysis pipeline: `python3 scripts/ir_analysis.py --staging --json --per-task --correlate` (output stored at `runs/staging/IR_ANALYSIS_STAGING_20260224.json`).
- IR pipeline note: `scripts/ir_analysis.py` has been patched to support staging/new config pairs and preserve SDLC suite labels. This report still computes additional staging-specific paired retrieval-effectiveness slices from the pipeline `per_task` output (task-level-valid MCP subset, situation buckets, and joined ranked table annotations).

## MCP Delta Audit Summary (Task-Level Validity)

- Runs scanned: **22**
- Pairable runs analyzed: **21**
- Matched task pairs: **193**
- Valid task pairs (non-infra + comparable): **177**
- Excluded task pairs: **16**
- Positive MCP deltas: **62**

### Task-Level Exclusions Applied

| Exclusion | Count |
|-----------|------:|
| `bl:docker_compose_fail` | 10 |
| `missing_reward` | 3 |
| `mcp:docker_compose_fail` | 2 |
| `bl:token_refresh_403` | 1 |

### Run Coverage

| Run | Suite | Matched | Valid | Excluded | MCP Wins |
|-----|------|-------:|-----:|--------:|--------:|
| `build_haiku_20260223_124805` | `ccb_build` | 25 | 25 | 0 | 9 |
| `debug_haiku_20260223_154724` | `ccb_debug` | 20 | 20 | 0 | 2 |
| `design_haiku_20260223_124652` | `ccb_design` | 20 | 20 | 0 | 10 |
| `document_haiku_20260223_164240` | `ccb_document` | 19 | 19 | 0 | 5 |
| `fix_haiku_20260223_171232` | `ccb_fix` | 24 | 21 | 3 | 7 |
| `fix_haiku_20260224_011821` | `ccb_fix` | 2 | 2 | 0 | 1 |
| `ccb_mcp_compliance_opus_20260223_193904` | `ccb_mcp_compliance` | 0 | 0 | 0 | 0 |
| `ccb_mcp_crossorg_haiku_20260221_140913` | `ccb_mcp_crossorg` | 2 | 2 | 0 | 1 |
| `ccb_mcp_crossrepo_tracing_haiku_20260221_140913` | `ccb_mcp_crossrepo_tracing` | 3 | 3 | 0 | 0 |
| `ccb_mcp_incident_haiku_20260221_140913` | `ccb_mcp_incident` | 1 | 1 | 0 | 1 |
| `ccb_mcp_migration_opus_20260223_193910` | `ccb_mcp_migration` | 0 | 0 | 0 | 0 |
| `ccb_mcp_onboarding_haiku_20260221_140913` | `ccb_mcp_onboarding` | 3 | 3 | 0 | 2 |
| `ccb_mcp_platform_haiku_20260221_140913` | `ccb_mcp_platform` | 1 | 1 | 0 | 0 |
| `ccb_mcp_security_haiku_20260221_140913` | `ccb_mcp_security` | 2 | 2 | 0 | 2 |
| `ccb_secure_opus_20260223_210902` | `ccb_secure` | 0 | 0 | 0 | 0 |
| `secure_haiku_20260223_232545` | `ccb_secure` | 20 | 18 | 2 | 6 |
| `ccb_test_opus_20260223_203633` | `ccb_test` | 0 | 0 | 0 | 0 |
| `test_haiku_20260223_235732` | `ccb_test` | 20 | 9 | 11 | 4 |
| `test_haiku_20260224_011816` | `ccb_test` | 11 | 11 | 0 | 3 |
| `ccb_understand_opus_20260223_203639` | `ccb_understand` | 0 | 0 | 0 | 0 |
| `understand_haiku_20260224_001815` | `ccb_understand` | 20 | 20 | 0 | 9 |

## IR Analysis Pipeline Output (Staging)

- Pipeline runs analyzed: **276** IR records
- Tasks with ground truth: **165**
- Included in IR aggregates (`--min-confidence=medium`): **241**
- Excluded low-confidence IR records from aggregates: **35**
- Skipped (no ground truth): **50**
- Skipped (no transcript): **12**

### Aggregate Retrieval Quality (Pipeline)

| Metric | Baseline (`baseline-local-direct`) | MCP (`mcp-remote-direct`) | Delta | % Change | Direction |
|--------|-----------------------------------:|---------------------------:|------:|---------:|-----------|
| `mrr` | 0.360 | 0.329 | -0.031 | -8.6% | higher is better |
| `map_score` | 0.217 | 0.191 | -0.026 | -12.0% | higher is better |
| `file_recall` | 0.339 | 0.438 | 0.098 | +28.9% | higher is better |
| `context_efficiency` | 0.187 | 0.160 | -0.027 | -14.5% | higher is better |
| `ttfr_median` | 12.700 | 7.900 | -4.800 | -37.8% | lower is better |
| `tt_all_r_median` | 22.200 | 9.600 | -12.600 | -56.8% | lower is better |
| `steps_to_first_median` | 3.000 | 2.000 | -1.000 | -33.3% | lower is better |

## Staging-Specific Retrieval Effectiveness Additions (From IR `per_task`)

These are the pairing-aware additions requested: they are computed directly from the IR pipeline `per_task` output for matched `baseline-local-direct` vs `mcp-remote-direct` task IDs (medium+ GT confidence only).

### Across All Direct Paired Tasks (Medium+ Confidence)

- Matched direct IR pairs: **114**
- MCP improves file recall on **35.1%** of paired tasks; mean delta **0.106**.
- MCP improves MRR on **31.6%** of paired tasks; mean delta **-0.045**.
- MCP reaches first relevant context faster (TTFR, lower is better) on **75.0%** of paired tasks; median delta **-6.000s**.
- MCP reduces agent-time-to-first-relevant on **76.1%** of paired tasks; median delta **-4.350s**.
- MCP changes cost-before-first-relevant on paired tasks (lower is better on 43.8% of tasks); median delta **+$0.0737**.
- MCP reduces tokens-before-first-relevant on **54.2%** of paired tasks; median delta **-7179.500** tokens.

### Within Positive MCP Outcome Deltas (Direct Tasks, Medium+ Confidence)

- Positive MCP direct tasks with IR join: **35**
- Mean MRR delta on positive-outcome tasks: **-0.009**
- Mean file-recall delta on positive-outcome tasks: **0.161**
- Mean context-efficiency delta on positive-outcome tasks: **0.010** (negative means broader context with more noise)
- Median TTFR delta on positive-outcome tasks: **-4.800s**
- Median agent-time-to-first-relevant delta on positive-outcome tasks: **-4.200s**
- Median cost-before-first-relevant delta on positive-outcome tasks: **$0.3790**
- Median tokens-before-first-relevant delta on positive-outcome tasks: **69735**

### Retrieval-Outcome Coupling (Staging Direct Pairs, Spearman)

| Relationship | n | rho | p-value |
|--------------|--:|----:|--------:|
| `all valid direct reward delta vs mrr delta` | 113 | +0.130 | 0.1667 |
| `all valid direct reward delta vs file recall delta` | 113 | +0.170 | 0.0686 |
| `all valid direct mcp reward vs mcp file recall` | 113 | +0.107 | 0.2570 |
| `positive direct reward delta vs mrr delta` | 35 | +0.067 | 0.6986 |
| `positive direct reward delta vs file recall delta` | 35 | -0.141 | 0.4143 |

## Situations Where MCP Added Value (Direct Tasks With IR Evidence)

The same positive reward delta can come from different retrieval behaviors. The buckets below help separate those situations.

### Retrieval rescue (baseline at 0, MCP finds relevant context and scores)

- Count: **4** (medium+ confidence direct positive tasks)

| Task | Suite | Reward Δ | MRR Δ | File Recall Δ | Ctx Eff Δ | TTFR Δ (s) | Agent TTFR Δ (s) |
|------|------|---------:|------:|--------------:|----------:|-----------:|-----------------:|
| `envoy-ext-authz-handoff-001` | `ccb_understand` | +0.830 | 1.000 | 0.400 | 0.174 | N/A | N/A |
| `kafka-producer-bufpool-fix-001` | `ccb_fix` | +0.780 | 1.000 | 0.556 | 0.263 | N/A | N/A |
| `ghost-code-review-001` | `ccb_test` | +0.620 | 1.000 | 1.000 | 0.039 | N/A | N/A |
| `aspnetcore-code-review-001` | `ccb_test` | +0.460 | 1.000 | 1.000 | 0.069 | N/A | N/A |

### Speed-to-context win (MCP reaches relevant context materially faster and outcome improves)

- Count: **6** (medium+ confidence direct positive tasks)

| Task | Suite | Reward Δ | MRR Δ | File Recall Δ | Ctx Eff Δ | TTFR Δ (s) | Agent TTFR Δ (s) |
|------|------|---------:|------:|--------------:|----------:|-----------:|-----------------:|
| `flipt-flagexists-refactor-001` | `ccb_build` | +0.300 | 0.000 | 0.000 | 0.098 | -51.200 | -51.500 |
| `django-repo-scoped-access-001` | `ccb_secure` | +0.200 | -0.357 | 0.000 | -0.210 | -24.300 | -25.700 |
| `kafka-message-lifecycle-qa-001` | `ccb_understand` | +0.140 | -0.667 | 0.000 | -0.076 | -65.800 | -64.600 |
| `django-select-for-update-fix-001` | `ccb_fix` | +0.110 | -0.950 | 0.222 | -0.428 | -13.500 | -8.100 |
| `k8s-dra-scheduler-event-fix-001` | `ccb_fix` | +0.070 | 0.000 | 0.250 | -0.145 | -5.900 | -7.200 |
| `postgres-client-auth-audit-001` | `ccb_secure` | +0.030 | -0.667 | 0.125 | -0.656 | -7.200 | -4.100 |

### Broader search win (recall up, context efficiency down, but reward still improves)

- Count: **5** (medium+ confidence direct positive tasks)

| Task | Suite | Reward Δ | MRR Δ | File Recall Δ | Ctx Eff Δ | TTFR Δ (s) | Agent TTFR Δ (s) |
|------|------|---------:|------:|--------------:|----------:|-----------:|-----------------:|
| `cilium-project-orient-001` | `ccb_understand` | +0.960 | -0.967 | 0.048 | -0.165 | -4.800 | -5.000 |
| `strata-fx-european-refac-001` | `ccb_build` | +0.480 | -0.957 | 0.286 | -0.188 | 11.900 | 13.400 |
| `django-select-for-update-fix-001` | `ccb_fix` | +0.110 | -0.950 | 0.222 | -0.428 | -13.500 | -8.100 |
| `k8s-dra-scheduler-event-fix-001` | `ccb_fix` | +0.070 | 0.000 | 0.250 | -0.145 | -5.900 | -7.200 |
| `postgres-client-auth-audit-001` | `ccb_secure` | +0.030 | -0.667 | 0.125 | -0.656 | -7.200 | -4.100 |

### Higher-quality context win (context efficiency up and reward improves)

- Count: **16** (medium+ confidence direct positive tasks)

| Task | Suite | Reward Δ | MRR Δ | File Recall Δ | Ctx Eff Δ | TTFR Δ (s) | Agent TTFR Δ (s) |
|------|------|---------:|------:|--------------:|----------:|-----------:|-----------------:|
| `terraform-plan-pipeline-qa-001` | `ccb_understand` | +0.950 | 0.006 | 0.167 | 0.003 | N/A | N/A |
| `envoy-ext-authz-handoff-001` | `ccb_understand` | +0.830 | 1.000 | 0.400 | 0.174 | N/A | N/A |
| `argocd-arch-orient-001` | `ccb_understand` | +0.810 | 0.019 | 0.000 | 0.001 | N/A | N/A |
| `kafka-producer-bufpool-fix-001` | `ccb_fix` | +0.780 | 1.000 | 0.556 | 0.263 | N/A | N/A |
| `terraform-state-backend-handoff-001` | `ccb_understand` | +0.630 | 0.035 | 0.118 | 0.048 | N/A | N/A |
| `ghost-code-review-001` | `ccb_test` | +0.620 | 1.000 | 1.000 | 0.039 | N/A | N/A |
| `aspnetcore-code-review-001` | `ccb_test` | +0.460 | 1.000 | 1.000 | 0.069 | N/A | N/A |
| `kafka-batch-accumulator-refac-001` | `ccb_build` | +0.360 | 0.000 | -0.455 | 0.135 | -0.500 | -2.000 |

### Execution/quality win after similar retrieval (retrieval nearly flat, reward still improves)

- Count: **10** (medium+ confidence direct positive tasks)

| Task | Suite | Reward Δ | MRR Δ | File Recall Δ | Ctx Eff Δ | TTFR Δ (s) | Agent TTFR Δ (s) |
|------|------|---------:|------:|--------------:|----------:|-----------:|-----------------:|
| `numpy-dtype-localize-001` | `ccb_understand` | +0.933 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `envoy-request-routing-qa-001` | `ccb_understand` | +0.870 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `argocd-arch-orient-001` | `ccb_understand` | +0.810 | 0.019 | 0.000 | 0.001 | N/A | N/A |
| `etcd-grpc-api-upgrade-001` | `ccb_design` | +0.714 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `grpcurl-transitive-vuln-001` | `ccb_secure` | +0.670 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `openlibrary-solr-boolean-fix-001` | `ccb_fix` | +0.667 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `grafana-table-panel-regression-001` | `ccb_debug` | +0.300 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| `flipt-flagexists-refactor-001` | `ccb_build` | +0.300 | 0.000 | 0.000 | 0.098 | -51.200 | -51.500 |

## Positive MCP Delta Tasks (Ranked)

All valid task pairs ranked by reward delta. IR columns are populated for direct tasks covered by the IR pipeline; artifact-suite tasks will show `N/A`.

| Rank | Reward Δ | Task | Suite | Run | BL | MCP | MRR Δ | Recall Δ | CtxEff Δ | TTFR Δ (s) | AgentTTFR Δ (s) |
|-----:|---------:|------|------|-----|---:|----:|------:|---------:|---------:|-----------:|----------------:|
| 1 | **+0.960** | `cilium-project-orient-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.960 | -0.967 | 0.048 | -0.165 | -4.800 | -5.000 |
| 2 | **+0.950** | `terraform-plan-pipeline-qa-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.950 | 0.006 | 0.167 | 0.003 | N/A | N/A |
| 3 | **+0.933** | `numpy-dtype-localize-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.933 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 4 | **+0.900** | `k8s-dra-allocation-impact-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.900 | N/A | N/A | N/A | N/A | N/A |
| 5 | **+0.880** | `test-coverage-gap-001` | `ccb_test` | `test_haiku_20260224_011816` | 0.060 | 0.940 | N/A | N/A | N/A | N/A | N/A |
| 6 | **+0.870** | `envoy-request-routing-qa-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.870 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 7 | **+0.830** | `envoy-ext-authz-handoff-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.830 | 1.000 | 0.400 | 0.174 | N/A | N/A |
| 8 | **+0.810** | `argocd-arch-orient-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.810 | 0.019 | 0.000 | 0.001 | N/A | N/A |
| 9 | **+0.780** | `kafka-producer-bufpool-fix-001` | `ccb_fix` | `fix_haiku_20260224_011821` | 0.000 | 0.780 | 1.000 | 0.556 | 0.263 | N/A | N/A |
| 10 | **+0.770** | `k8s-crd-lifecycle-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.770 | N/A | N/A | N/A | N/A | N/A |
| 11 | **+0.730** | `camel-routing-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.730 | N/A | N/A | N/A | N/A | N/A |
| 12 | **+0.730** | `flink-checkpoint-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.730 | N/A | N/A | N/A | N/A | N/A |
| 13 | **+0.720** | `k8s-scheduler-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.720 | N/A | N/A | N/A | N/A | N/A |
| 14 | **+0.714** | `etcd-grpc-api-upgrade-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.714 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 15 | **+0.710** | `rust-subtype-relation-refac-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.000 | 0.710 | N/A | N/A | N/A | N/A | N/A |
| 16 | **+0.670** | `grpcurl-transitive-vuln-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.000 | 0.670 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 17 | **+0.667** | `openlibrary-solr-boolean-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.000 | 0.667 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 18 | **+0.630** | `terraform-state-backend-handoff-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.000 | 0.630 | 0.035 | 0.118 | 0.048 | N/A | N/A |
| 19 | **+0.620** | `ghost-code-review-001` | `ccb_test` | `test_haiku_20260224_011816` | 0.000 | 0.620 | 1.000 | 1.000 | 0.039 | N/A | N/A |
| 20 | **+0.530** | `test-integration-002` | `ccb_test` | `test_haiku_20260223_235732` | 0.370 | 0.900 | N/A | N/A | N/A | N/A | N/A |
| 21 | **+0.520** | `test-unitgen-py-001` | `ccb_test` | `test_haiku_20260223_235732` | 0.480 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 22 | **+0.500** | `ccx-crossorg-061` | `ccb_mcp_crossorg` | `ccb_mcp_crossorg_haiku_20260221_140913` | 0.500 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 23 | **+0.500** | `ccx-incident-031` | `ccb_mcp_incident` | `ccb_mcp_incident_haiku_20260221_140913` | 0.500 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 24 | **+0.480** | `strata-fx-european-refac-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.320 | 0.800 | -0.957 | 0.286 | -0.188 | 11.900 | 13.400 |
| 25 | **+0.460** | `aspnetcore-code-review-001` | `ccb_test` | `test_haiku_20260224_011816` | 0.000 | 0.460 | 1.000 | 1.000 | 0.069 | N/A | N/A |
| 26 | **+0.400** | `kafka-flink-streaming-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.000 | 0.400 | N/A | N/A | N/A | N/A | N/A |
| 27 | **+0.393** | `ccx-vuln-remed-014` | `ccb_mcp_security` | `ccb_mcp_security_haiku_20260221_140913` | 0.250 | 0.643 | N/A | N/A | N/A | N/A | N/A |
| 28 | **+0.390** | `flink-pricing-window-feat-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.120 | 0.510 | N/A | N/A | N/A | N/A | N/A |
| 29 | **+0.380** | `test-unitgen-go-001` | `ccb_test` | `test_haiku_20260223_235732` | 0.620 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 30 | **+0.360** | `kafka-batch-accumulator-refac-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.320 | 0.680 | 0.000 | -0.455 | 0.135 | -0.500 | -2.000 |
| 31 | **+0.340** | `k8s-typemeta-dep-chain-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.330 | 0.670 | 0.067 | 1.000 | 0.037 | N/A | N/A |
| 32 | **+0.333** | `openlibrary-fntocli-adapter-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.667 | 1.000 | 1.000 | 0.071 | 0.500 | N/A | N/A |
| 33 | **+0.300** | `docgen-changelog-002` | `ccb_document` | `document_haiku_20260223_164240` | 0.700 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 34 | **+0.300** | `grafana-table-panel-regression-001` | `ccb_debug` | `debug_haiku_20260223_154724` | 0.600 | 0.900 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 35 | **+0.300** | `flipt-flagexists-refactor-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.450 | 0.750 | 0.000 | 0.000 | 0.098 | -51.200 | -51.500 |
| 36 | **+0.250** | `ccx-vuln-remed-011` | `ccb_mcp_security` | `ccb_mcp_security_haiku_20260221_140913` | 0.750 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 37 | **+0.250** | `ccx-onboard-050-ds` | `ccb_mcp_onboarding` | `ccb_mcp_onboarding_haiku_20260221_140913` | 0.250 | 0.500 | N/A | N/A | N/A | N/A | N/A |
| 38 | **+0.200** | `k8s-score-normalizer-refac-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.580 | 0.780 | N/A | N/A | N/A | N/A | N/A |
| 39 | **+0.200** | `django-cross-team-boundary-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.300 | 0.500 | -0.474 | 0.000 | -0.178 | -4.300 | -4.200 |
| 40 | **+0.200** | `django-repo-scoped-access-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.500 | 0.700 | -0.357 | 0.000 | -0.210 | -24.300 | -25.700 |
| 41 | **+0.180** | `prometheus-queue-reshard-debug-001` | `ccb_debug` | `debug_haiku_20260223_154724` | 0.420 | 0.600 | 0.960 | -0.250 | 0.954 | 0.500 | 0.200 |
| 42 | **+0.170** | `terraform-arch-doc-gen-001` | `ccb_document` | `document_haiku_20260223_164240` | 0.420 | 0.590 | N/A | N/A | N/A | N/A | N/A |
| 43 | **+0.167** | `ccx-explore-042-ds` | `ccb_mcp_onboarding` | `ccb_mcp_onboarding_haiku_20260221_140913` | 0.667 | 0.833 | N/A | N/A | N/A | N/A | N/A |
| 44 | **+0.140** | `kafka-message-lifecycle-qa-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.860 | 1.000 | -0.667 | 0.000 | -0.076 | -65.800 | -64.600 |
| 45 | **+0.140** | `envoy-migration-doc-gen-001` | `ccb_document` | `document_haiku_20260223_164240` | 0.650 | 0.790 | 0.062 | 1.000 | 0.059 | N/A | N/A |
| 46 | **+0.110** | `django-select-for-update-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.670 | 0.780 | -0.950 | 0.222 | -0.428 | -13.500 | -8.100 |
| 47 | **+0.100** | `django-rate-limit-design-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.900 | 1.000 | -0.179 | 0.000 | -0.179 | -3.800 | -1.100 |
| 48 | **+0.100** | `envoy-cve-triage-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.900 | 1.000 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 49 | **+0.080** | `django-orm-query-arch-001` | `ccb_design` | `design_haiku_20260223_124652` | 0.910 | 0.990 | -0.875 | 0.000 | -0.248 | N/A | N/A |
| 50 | **+0.070** | `k8s-dra-scheduler-event-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.680 | 0.750 | 0.000 | 0.250 | -0.145 | -5.900 | -7.200 |
| 51 | **+0.060** | `test-coverage-gap-002` | `ccb_test` | `test_haiku_20260223_235732` | 0.940 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 52 | **+0.060** | `kafka-vuln-reachability-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.860 | 0.920 | 1.000 | 1.000 | 0.167 | N/A | N/A |
| 53 | **+0.057** | `ansible-abc-imports-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.943 | 1.000 | -0.929 | -0.636 | -0.465 | 7.500 | 8.900 |
| 54 | **+0.050** | `cilium-ebpf-fault-qa-001` | `ccb_understand` | `understand_haiku_20260224_001815` | 0.770 | 0.820 | 0.000 | 0.000 | 0.000 | N/A | N/A |
| 55 | **+0.040** | `python-http-class-naming-refac-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.840 | 0.880 | 0.100 | 0.500 | 0.312 | N/A | N/A |
| 56 | **+0.040** | `envoy-grpc-server-impl-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.400 | 0.440 | 0.500 | 0.500 | 0.286 | N/A | N/A |
| 57 | **+0.030** | `postgres-client-auth-audit-001` | `ccb_secure` | `secure_haiku_20260223_232545` | 0.740 | 0.770 | -0.667 | 0.125 | -0.656 | -7.200 | -4.100 |
| 58 | **+0.020** | `vscode-api-doc-gen-001` | `ccb_document` | `document_haiku_20260223_164240` | 0.980 | 1.000 | N/A | N/A | N/A | N/A | N/A |
| 59 | **+0.020** | `cilium-api-doc-gen-001` | `ccb_document` | `document_haiku_20260223_164240` | 0.960 | 0.980 | N/A | N/A | N/A | N/A | N/A |
| 60 | **+0.010** | `k8s-runtime-object-impl-001` | `ccb_build` | `build_haiku_20260223_124805` | 0.110 | 0.120 | 0.021 | 0.667 | 0.028 | N/A | N/A |
| 61 | **+0.008** | `flipt-ecr-auth-oci-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.987 | 0.995 | 0.026 | 0.667 | 0.118 | N/A | N/A |
| 62 | **+0.001** | `flipt-otlp-exporter-fix-001` | `ccb_fix` | `fix_haiku_20260223_171232` | 0.978 | 0.979 | 0.053 | 0.393 | 0.250 | N/A | N/A |

## IR-Backed MCP Value Spotlights

### `ghost-code-review-001` (ccb_test)

- Run: `test_haiku_20260224_011816`
- Reward delta: **+0.620** (BL 0.000 -> MCP 0.620)
- Retrieval deltas: MRR 1.000, file recall 1.000, context efficiency 0.039
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `aspnetcore-code-review-001` (ccb_test)

- Run: `test_haiku_20260224_011816`
- Reward delta: **+0.460** (BL 0.000 -> MCP 0.460)
- Retrieval deltas: MRR 1.000, file recall 1.000, context efficiency 0.069
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `kafka-producer-bufpool-fix-001` (ccb_fix)

- Run: `fix_haiku_20260224_011821`
- Reward delta: **+0.780** (BL 0.000 -> MCP 0.780)
- Retrieval deltas: MRR 1.000, file recall 0.556, context efficiency 0.263
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `envoy-ext-authz-handoff-001` (ccb_understand)

- Run: `understand_haiku_20260224_001815`
- Reward delta: **+0.830** (BL 0.000 -> MCP 0.830)
- Retrieval deltas: MRR 1.000, file recall 0.400, context efficiency 0.174
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `openlibrary-fntocli-adapter-fix-001` (ccb_fix)

- Run: `fix_haiku_20260223_171232`
- Reward delta: **+0.333** (BL 0.667 -> MCP 1.000)
- Retrieval deltas: MRR 1.000, file recall 0.071, context efficiency 0.500
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `prometheus-queue-reshard-debug-001` (ccb_debug)

- Run: `debug_haiku_20260223_154724`
- Reward delta: **+0.180** (BL 0.420 -> MCP 0.600)
- Retrieval deltas: MRR 0.960, file recall -0.250, context efficiency 0.954
- Time-to-context deltas: TTFR 0.500s, TTAR N/A, steps-to-first 0.000 (lower is better)
- Retrieval-effectiveness additions: agent TTFR 0.200s, cost-before-first-relevant $0.3465, tokens-before-first-relevant 80514.000, output-tokens-before-first-relevant -8.000

### `terraform-plan-pipeline-qa-001` (ccb_understand)

- Run: `understand_haiku_20260224_001815`
- Reward delta: **+0.950** (BL 0.000 -> MCP 0.950)
- Retrieval deltas: MRR 0.006, file recall 0.167, context efficiency 0.003
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `envoy-grpc-server-impl-001` (ccb_build)

- Run: `build_haiku_20260223_124805`
- Reward delta: **+0.040** (BL 0.400 -> MCP 0.440)
- Retrieval deltas: MRR 0.500, file recall 0.500, context efficiency 0.286
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

### `cilium-project-orient-001` (ccb_understand)

- Run: `understand_haiku_20260224_001815`
- Reward delta: **+0.960** (BL 0.000 -> MCP 0.960)
- Retrieval deltas: MRR -0.967, file recall 0.048, context efficiency -0.165
- Time-to-context deltas: TTFR -4.800s, TTAR N/A, steps-to-first -7.000 (lower is better)
- Retrieval-effectiveness additions: agent TTFR -5.000s, cost-before-first-relevant $-0.1588, tokens-before-first-relevant -167453.000, output-tokens-before-first-relevant -12.000

### `numpy-dtype-localize-001` (ccb_understand)

- Run: `understand_haiku_20260224_001815`
- Reward delta: **+0.933** (BL 0.000 -> MCP 0.933)
- Retrieval deltas: MRR 0.000, file recall 0.000, context efficiency 0.000
- Time-to-context deltas: TTFR N/A, TTAR N/A, steps-to-first N/A (lower is better)
- Retrieval-effectiveness additions: agent TTFR N/A, cost-before-first-relevant $N/A, tokens-before-first-relevant N/A, output-tokens-before-first-relevant N/A

## Artifacts Generated

- Main report: `runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224.md`
- MCP valid-task delta JSON: `runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224.json`
- IR pipeline JSON: `runs/staging/IR_ANALYSIS_STAGING_20260224.json`
- IR pipeline markdown (auto-generated): `docs/ir_analysis_report.md`
- Staging IR enrichment JSON (this report's computed additions): `runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224_ir_enrichment.json`
