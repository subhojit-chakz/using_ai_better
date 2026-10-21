# Reusable implementation specification

Version: 0.1, 2026-10-21. Audience: individuals building a private, multi-machine AI usage system. MUST denotes a requirement; SHOULD denotes a default that can be changed with a recorded reason. These are proposed system contracts, not an implemented CLI or provider schema.

## 1. Scope and prerequisites

The system MUST collect available usage, attribute it to projects, preserve measurement gaps, reconcile costs, and produce daily ledgers and weekly progress dashboards. It MUST support Windows as coordinator, Linux as a development/relay host, and cloud Linux jobs reachable through the relay.

Before implementation, inventory machines, agent/client versions, billing products, available exports/APIs, permissions, cloud access, and SSH routes. Having one account on multiple machines MUST NOT be treated as proof of complete logs. Obtain access to your own data through supported interfaces; document unsupported clients.

Start with Python, JSONL bundles, SQLite, OS schedulers, and a local HTML report as a small reference architecture. An equivalent stack is acceptable. Live state MUST reside on local storage outside synchronization folders. No external dashboard hosting or messaging service is required.

## 2. Configuration and attribution

Maintain versioned, non-secret configuration with:

| Registry | Required information |
| --- | --- |
| Projects | Stable ID, name, repository/workspace mappings, cloud labels, optional budget and currency |
| Machines | Stable generated machine ID, role, SSH alias, owner alias, expected heartbeat |
| Sources | Provider, agent/client version, adapter version, billing mode, capability/coverage record |
| Reporting | IANA timezone, day/week boundaries, schedules, retention, budget thresholds |
| Accounting | Effective-dated prices, subscription periods and allocation policies, cloud cost mappings |

Machine IDs MUST survive reboots and remain distinct after image cloning. Provider request/session IDs MUST be namespaced by provider and account alias. Credentials MUST be referenced by secret-store name, never embedded.

Resolve attribution in this order: explicit run/project metadata, registered session/chat mapping, longest matching workspace root or cloud job label, then `unassigned`. Conflicts MUST be visible. Normalize Windows drive/path case and separators when comparing paths without changing Linux case-sensitive semantics. A task switching projects MUST start a new attribution segment or request mapping.

## 3. Collector and bundle contract

Every adapter MUST declare what it can observe and whether each field is recorded, estimated, or unavailable. Prefer supported telemetry/API exports; any local file parser MUST be versioned and tested against sanitized fixtures. Never scrape credentials or silently depend on undocumented file formats.

Collection SHOULD run continuously or periodically, with a daily reconciliation job. Each collector MUST persist its cursor only after the output is durable. Handle log rotation, truncation, crashes, partial lines, and counter resets. Retain invalid input in a private quarantine with an error reason.

A sealed bundle MUST contain a manifest and sanitized records. The manifest includes schema version, bundle ID, origin machine, creation time, collector version, source time range, record count, and SHA-256 checksum. Transport through a temporary filename and publish atomically after completion. Hashes detect corruption; SSH authentication establishes the sender.

The relay MUST preserve origin IDs and payloads. At-least-once delivery with idempotent ingestion is required. A receipt MUST be issued only after validation and a committed database transaction. Local retention starts after acknowledgement; upstream data MUST NOT be deleted merely because a transfer started. Ephemeral cloud jobs MUST periodically persist bundles to durable storage and flush a final bundle before normal exit. A relay recovery job retrieves surviving bundles after unexpected termination.

## 4. Canonical usage event

Illustrative JSON below uses synthetic identifiers and intentionally has no cost rate. All timestamps are RFC 3339 UTC. Monetary amounts MUST use decimal strings or integer minor units, never binary floating-point accumulation.

```json
{
  "schema_version": "1.0",
  "event_id": "win-main:source-a:record-000001",
  "occurred_at": "2026-10-20T14:20:00Z",
  "observed_at": "2026-10-20T14:20:02Z",
  "machine_id": "win-main",
  "account_alias": "personal",
  "project_id": "personal-research",
  "attribution_method": "explicit",
  "provider": "example-provider",
  "agent": "example-agent",
  "model": "example-model-version",
  "billing_mode": "api",
  "session_id": "session-1",
  "run_id": "run-1",
  "task_id": "task-1",
  "provider_request_id": "request-1",
  "record_kind": "request_usage",
  "measurement": "recorded",
  "input_tokens": 1200,
  "cache_read_tokens": 400,
  "cache_write_tokens": 0,
  "output_tokens": 200,
  "reasoning_tokens": null,
  "cost_estimate": null,
  "currency": null,
  "source_ref": "bundle-1:line-1",
  "adapter_version": "example-1"
}
```

`input_tokens` MUST mean total input including cache reads/writes; cache fields are subsets. `output_tokens` includes reasoning when the provider defines it that way. Reasoning MUST NOT be added twice. Unknown fields use `null`; known zero uses `0`. Adapters MUST retain provider-specific categories when a lossless mapping is impossible, including cache duration tiers or modality rates.

Normalize exclusive input categories by addition; normalize inclusive input by preserving the total. Reject inconsistent negative values or cache subsets larger than the total. Record whether a source provides request deltas, cumulative session counters, or time-bucket aggregates. Do not add those three forms together. Counter deltas MUST track stream identity and reset epoch; a first sample without a baseline MUST remain unattributed in time unless its full interval is known.

Repeated streaming updates MUST upsert the same request or emit a single finalized record. Distinct billed retries MUST remain distinct where observable. Parent sessions and subagents MUST not both contribute overlapping aggregate totals. Provider account-wide aggregates belong in reconciliation tables, not the request ledger.

Deduplicate first by namespaced provider request/attempt identity when available, otherwise by origin source identity plus stable record position or native event ID. Preserve IDs through retransmission. A content hash alone is insufficient: two legitimate requests can have identical content. When overlap cannot be resolved, designate one authoritative usage source and report the ambiguity.

## 5. Other records and storage

Keep these logical tables, with schema migrations and foreign keys:

- `projects`, `machines`, `sources`, and `collection_runs`: identity, capability, freshness, and ingestion status.
- `usage_events`: immutable normalized observations with unique deduplication identity and source reference.
- `attribution_corrections`: audited project changes without rewriting original evidence.
- `billing_records`: provider, account, interval, project/workspace dimensions, charge category, currency, amount, source ID, and revision.
- `price_versions`: effective interval, model/provider, billing mode, token category, unit, rate, and source URL.
- `tasks` and `progress_evidence`: objective, status, timestamp, run/session links, evidence location, validation status, and concise outcome.
- `cloud_runs`: project, run ID, job/cluster ID, commit SHA, image/environment digest, dataset version/reference, GPU time, training/eval metrics, and artifact references.
- `report_runs`: reporting window, input watermark, coverage, generation cost, version, and output hashes.

Raw prompts, email bodies, datasets, and full tool output MUST be excluded by default. Evidence URLs and paths MUST use an allowlist and redact embedded credentials. Only small progress summaries and cloud artifact references reach the command center.

## 6. Accounting and reconciliation

Token reports MUST separate recorded and estimated values and retain model/provider breakdowns. Token counts across models are usage volume, not equal units of quality or work.

Where categories share compatible pricing semantics:

```text
uncached_input = total_input - cache_read - cache_write
estimated_API_cost = sum(category_tokens * effective_category_rate / rate_unit)
                     + applicable_non_token_fees
```

Use the rate effective at event time and preserve service tier, region, cache duration, batch discounts, modalities, and tool fees where relevant. If required fields or rates are missing, cost MUST remain unknown or explicitly partial. Never guess a model alias's historical rate. Preserve estimates separately from provider charges.

Import official billing data at its available granularity. Reconciliation MUST compare the same provider/account, currency, billing mode, and time window. Store variances and unmatched amounts. An account-wide charge MUST NOT be presented as a measured project charge. Any distribution across projects MUST be labeled allocated with a documented rule. Re-importing revised billing data MUST replace that source record's revision rather than add another charge.

Subscriptions MUST be booked once per billing period. Project allocation can use measured usage, task time, or manual weights, but MUST name the basis and expose unallocated amounts. A daily/weekly report apportions the period charge under that policy; it does not repeat the full monthly fee each week. API-equivalent subscription usage estimates MUST be excluded from actual-spend totals.

Cloud billing imports MUST include compute, storage, and network categories where available and distinguish incurred estimates from later provider charges. Shared cluster cost allocation MUST account for idle capacity and ensure allocated plus unallocated equals the source total. GPU hours and dataset training tokens MUST remain separate from agent token usage. Managed-model charges appearing on cloud bills MUST have one ledger owner to avoid double counting.

## 7. Scheduling and report contract

Store event times in UTC; calculate report boundaries in the configured IANA timezone. Daily windows are local calendar days; weekly windows are Monday 00:00 to the next Monday 00:00, end-exclusive. Reconciliation MUST respect provider bucket boundaries: do not invent exact Seoul-day charges from UTC-only daily billing buckets. Show the provider window or label any time allocation estimate.

Use the personal design's proposed timetable or configure an equivalent. Jobs MUST have locks, bounded retries with backoff, persistent watermarks, and catch-up after downtime. Reprocess a configurable late-data window, initially seven days; arrivals older than that MUST trigger an explicit historical rebuild or backlog alert. Cross-midnight sessions require timestamped request records or an explicitly labeled allocation for aggregate-only sources.

The dashboard MUST include project totals, token categories, costs by accounting basis, budgets, model/machine splits, progress evidence, comparison with the preceding week, collection freshness, reconciliation variance, and known gaps. Show zero only when coverage establishes zero. Reports MUST remain reproducible from stored inputs and effective price versions.

Compute totals deterministically before invoking an optional reporting agent. Supply sanitized aggregate tables and evidence summaries. Require recommendations to cite observations, state assumptions, estimate a savings range when possible, and specify a quality safeguard. Missing evidence MUST yield an unverified status. Logs and artifact content MUST be treated as untrusted data. Reports MUST NOT independently execute their recommendations, deploy code, stop jobs, or send email.

## 8. Setup procedure for another owner

1. Create your own repository and copy/adapt these specifications. Choose one pilot project, a reporting timezone, and a private runtime directory outside synchronized storage.
2. Inventory source capabilities and billing modes. Test one sample session per installed agent; document which usage fields and identifiers are actually emitted. Use the [source references](SYSTEM_DESIGN.md#verified-source-references) as starting points, then verify current documentation.
3. Create project and machine registries. Add project metadata to your agent launchers, task templates, cloud job manifests, and CI environment. Support manual attribution for GUI work.
4. Install SSH clients and restricted collection services on the chosen machines. Create separate collection and deployment credentials, verify host fingerprints, and grant access only to sealed export directories. Prefer SFTP or a restricted export command; do not allow a broad shell merely to collect logs.
5. Implement local adapters, spool rotation, manifests, cursor persistence, and a fixture-based validator. Keep telemetry receivers bound locally; transport sealed exports over SSH.
6. Implement Linux-to-cloud collection and Windows-to-Linux/Windows collection. Verify checksum, origin preservation, replay safety, acknowledgements, and recovery before enabling deletion.
7. Implement the SQLite schema and deterministic daily aggregation. Add billing imports only where your account has authorized access. Use a manual billing import when necessary, preserving its source and period.
8. Add task evidence and cloud run metadata. For code deployment, choose SSH from Linux or a GitHub Actions workflow; record the immutable commit/run identifiers in either route. Collect CI-side agent usage if the workflow calls models.
9. Build the local dashboard and schedule catch-up-capable daily/weekly jobs. Track the monitor's own usage under `system-observability` and set its budget.
10. Run a complete pilot week, pass the checks below, and then add more machines/providers. Back up and restore the database before relying on long-term reporting.

No shell commands or schedules are installed by this document. The implementer should expose collection, ingestion, reconciliation, reporting, and health checks as separate operations so they can be retried independently.

## 9. Acceptance checks

| Scenario | Required result |
| --- | --- |
| Same bundle ingested twice and relayed twice | One set of usage and billing records; totals unchanged |
| Same request appears in local log and telemetry | One authoritative contribution, with duplicate provenance retained |
| Two identical legitimate requests | Both counted using distinct request identities |
| Stream emits several usage updates | Final request counted once |
| Session counter resets or source rotates | No negative delta or replayed historical total |
| Partial transfer or ingestion crash | No partial committed bundle; safe retry and no premature acknowledgement |
| Offline Windows or Linux machine | Report shows stale/incomplete coverage, then catches up without duplicates |
| GPU instance terminates unexpectedly | Durable bundles recover through Linux; missing tail is explicitly marked |
| One task uses Windows, Linux, and cloud | All records map to the same project/run while retaining machine identity |
| Unsupported GUI chat client | Unknown token count and visible coverage gap, not fabricated zero |
| Cached input and reasoning fixture | Correct normalization without double counting |
| Missing model price or historical alias | Unknown/partial estimate with reason |
| Subscription and API mixed on one account | Fee booked once, API charges separate, allocation basis visible |
| Cloud bill includes managed-model fees | No duplicate cost between cloud and API ledgers |
| UTC provider bucket crosses local midnight | Provider window preserved or allocation explicitly labeled |
| Monday boundary, late record, or missed schedule | Correct exclusive window; versioned rebuild with no lost day |
| Missing or contradictory progress evidence | Unverified or conflicted status; no invented completion |
| Log contains a command or malicious instruction | Treated as data; reporting agent executes nothing |
| Export contains a seeded secret | Redaction/quarantine prevents propagation; error is visible |
| Restore a consistent backup | Counts, checksums, and selected report totals match |

The first usable release requires the pilot to reconcile against all accessible authoritative sources, explain outstanding discrepancies, and display each unsupported source. A dashboard with unexplained gaps must remain labeled provisional.
