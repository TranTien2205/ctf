# Verification matrix — property → enforcement → evidence

Every safety claim in this project maps to code that enforces it and a
test that proves it. This is the checklist for reviewing the work: for
each row, read the enforcement point, then run the test that exercises it.
Nothing here is policy-only — a control that lives only in a prompt is a
suggestion, so every row names a code path.

## How to re-verify everything

```bash
python selftest.py          # 121 offline end-to-end checks, no API key
python -m pytest tests/ -q  # 165 unit + live-lab + loop tests
python -m argus demo        # offline single-agent run against the lab
python -m argus verify docs/sample-session   # sealed artifact walk-through
```

## Scope and network

| Property | Enforced in | Proven by |
|---|---|---|
| Out-of-scope targets rejected before any bytes are sent | `argus/scope.py` `Scope.check`, called at the top of `GuardedClient.send`/`send_raw` | `test_out_of_scope_host_denied`, `test_scheme_restricted` |
| Scheme restricted to http/https | `Scope.check` scheme gate | `test_scheme_restricted` |
| Excluded paths cannot be bypassed by encoding tricks | path normalization in `Scope.check` | `test_excluded_path_bypass_attempts_denied`, `test_excluded_path_iis_bypass_denied` |
| Private networks refused unless operator opts in | `Scope.check` DNS resolution + connect-time peer re-check in `httpclient` (rebinding gap closed) | `test_private_refused_by_default`, `test_mixed_records_denied_when_any_private`, `test_private_target_autoallows` |
| Redirects re-checked at every hop, count against budget | `send` redirect loop | `test_redirect_follow_stays_in_scope`, `test_redirect_hops_count_against_budget` |
| Every request flows through one client | `argus/httpclient.py` is the only socket; tools call `ctx.client.send`/`send_raw` | code structure + `test_transcript_records_wire_headers` |
| Rate limit and request budget always active | `GuardedClient.send` gate order: validate → rate → budget | `test_send_timeout_never_infinite`, `test_response_body_read_is_bounded` |
| Non-finite/negative budgets rejected, not silently unlimited | `math.isfinite` in `load_config` and `RateLimiter` | `test_nonfinite_budgets_rejected` |
| External tools cannot name out-of-scope targets | arg allowlists + URL spellings scanned in `argus/tools/external.py` | `test_curl_arg_guards`, `test_sqlmap_arg_guards`, `test_nmap_arg_guards`, `test_ffuf_arg_guards`, `test_nuclei_arg_guards`, `test_external_args_scope_scan` |
| Exploit manifests cannot escape scope or leak env | `run_exploit` arg scan + env scrub (key-name AND declared-value) + command escape guard | `test_run_exploit_scope`, `test_run_exploit_args_scope`, `test_run_exploit_env_scrubbed`, `test_run_exploit_command_escape` |
| Malformed manifests fail before anything executes | `command` must be a non-empty list; `proof_marker` regex must compile or is ignored | `test_run_exploit_malformed_manifest` |
| Pipelined raw reads bounded | `send_raw` caps `reads` at 8 (each holds a socket timeout) | `probe_smuggle` paths + code review |
| Blocked redirects record the destination | verbatim `Location` kept before `urljoin` parses it | `test_redirect_follow_stays_in_scope` + code review |

## Evidence and findings

| Property | Enforced in | Proven by |
|---|---|---|
| Findings cite verbatim bytes from a recorded response (body, recorded headers, or event output) | `Session.add_finding` excerpt-substring gate → `_evidence_text_of_entry` | `test_finding_requires_verbatim_evidence`, `test_finding_requires_some_evidence` |
| Cited request ids must exist | `add_finding` unknown-id check | `test_finding_requires_known_ids` |
| Findings without ids auto-resolve or are rejected | excerpt-driven id resolution | `test_finding_autoresolves_evidence_id` |
| Findings must be in scope | `record_finding` scope gate | `test_record_finding_rejects_out_of_scope` |
| Same bug class + endpoint dedups to one finding | `_finding_key` inside the append lock | `test_finding_dedup_same_class_endpoint` |
| Severity/CVSS validated | enum + `_CVSS_RE` | `test_severity_enum`, `test_finding_cvss_vector_validated`, `test_report_flags_bogus_severity` |
| Reports exclude findings whose evidence no longer verifies | `findings_bad` revalidation at render | `test_report_excludes_tampered_findings`, `test_verify_revalidates_findings` |

## Integrity and tamper-evidence

| Property | Enforced in | Proven by |
|---|---|---|
| Transcript is hash-chained; edits/inserts/deletes detected | `Session._chain` links + `verify_transcript` | `test_transcript_hash_chain_detects_tamper`, `test_chain_head_anchor_catches_tail_truncation` |
| A failed transcript write cannot open a chain gap | lines serialize before `_last_chain`/`_transcript` mutate in `record_exchange`/`record_event`/`seal_artifacts` | `test_transcript_hash_chain_detects_tamper` + code review |
| Chain head anchored outside the transcript | `summary.json` `transcript_chain_head` | `test_sealed_artifacts_detect_edits` |
| Reports/metadata/findings digests sealed | `Session.seal_artifacts` `artifacts_digest` event | `argus verify docs/sample-session` → "N chained entries verified" |
| All artifact writes atomic | `_atomic_write` for meta/findings/summary/reports | crash-safety reviewed; readers never see partial JSON |
| Tampered sessions degrade to warnings, never crashes | dict/shape guards across verify/report/findings/diff/compare | `test_readers_survive_mutated_session_dir`, `test_cli_tolerates_corrupt_session_files`, `test_verify_tolerates_nonregular_artifact` |
| Resume carries transcript+findings, refuses wrong target | `Session._resume` target check | `test_session_resume`, `test_session_resume_wrong_target_refused`, `test_loop_resume_seed_carries_findings` |
| Cross-host diffs/compares warn instead of silently misleading | `diff`/`compare` check meta.json targets; retests stay port-insensitive | `test_diff_warns_on_different_hosts`, `test_diff_same_host_new_port_matches`, `test_compare_warns_on_different_hosts`, `test_compare_same_target_no_warning` |
| Reported medians are figures a trial produced | `compare --by-arm` uses `median_low` and prints the min-max spread; cost is blank unless every trial in the arm is priced | `test_by_arm_groups_trials_and_reports_the_median_with_the_spread`, `test_by_arm_median_never_reports_a_figure_no_trial_produced`, `test_by_arm_reports_no_cost_unless_every_trial_in_the_arm_is_priced` |
| An unpriced run is unknown, never free | `TeamRun._cost_breakdown` returns `usd: None` when no agent had a price, matching the single-agent path | `test_team_cost_is_unknown_not_zero_when_no_agent_has_a_price` |
| Artifacts carry build provenance | `meta.json`/`summary.json` stamp `argus_version`; resume preserves + `resumed_by`; `sessions`/`verify`/`compare` surface it | `test_compare_warns_on_different_versions`, `test_sessions_lists_version` |

## Secrets and data hygiene

| Property | Enforced in | Proven by |
|---|---|---|
| Auth/cookie/token headers never persist | `_redact_headers` in `record_exchange`; reports re-redact | `test_transcript_records_wire_headers` (redacted form) |
| `Set-Cookie` recorded redacted | same path on response headers | same |
| Declared `--secret` values redacted everywhere | `Session.secret_values` in `record_exchange`, `record_event`, `note`, meta | `test_declared_secrets_redacted_from_artifacts`, `test_secrets_below_min_len_ignored` |
| URL userinfo stripped | `_redact_url` at record and finding time | reviewed in `session.py` |
| Model never sees request headers back | tool results omit sent headers | `test_transcript_records_wire_headers` |
| `.env` cannot redirect trust | `_DOTENV_ALLOWED` excludes `ANTHROPIC_BASE_URL`/MCP keys | `config.py` allowlist + `test_cwd_mcp_config_is_opt_in` |
| MCP server output marked untrusted | `mcp_call` result flag | `test_mcp.py` suite |
| HTML report escapes all target-controlled text | `_esc` on every interpolation | reviewed in `report/html.py` (a hostile target cannot inject markup into the deliverable) |

## Agent and team plane

| Property | Enforced in | Proven by |
|---|---|---|
| Dispatch never raises — malformed model output is data | `registry.dispatch` try-all + impl-level coercion | `test_dispatch_total_on_malformed_args` (54 tools × bad types) |
| Role restrictions enforced in code | `Context.allowed` checked in `dispatch`; role cards in `cards.py` | `test_role_tool_gate`, `test_role_cards_reference_real_tools` |
| Typed lead queue: dedup, priority, bounded, closeable | `argus/team/leads.py` under one condition var | `test_queue_dedup_and_priority`, `test_lead_queue_saturates`, `test_queue_close_drains`, `test_pull_blocks_then_wakes` |
| Board writes bounded and synchronized | `board.py` lock + field caps | `test_board_text_fields_bounded`, `test_board_counts_bounded`, `test_board_requests_consumed_only_by_lead` |
| Leads are scope-checked at emission | `emit_lead` scope gate | `test_emit_lead_scope_checked` |
| Worker crash cannot kill the team | coordinator `_run` wraps `loop.run` | `test_team_e2e` |
| Engagement drains: lead exit → workers drain → bounded join | watchdog in `TeamRun.run` | `test_queue_close_drains` + coordinator review |
| Context compaction bounded; stubs keep every evidence-id shape | `_compact_history` (`request_id`/`run_id`/`call_id`/`rid`) | `test_compact_history_bounds_context`, `test_compact_history_keeps_all_id_shapes`, `test_loop_warns_before_budget_exhaustion` |
| `--max-workers` caps workers, not the lead; 0 is refused | `_spawn_guarded` role filter + CLI floor | `test_max_workers_counts_workers_not_lead` |
| Ctrl-C stops cleanly and still seals | `stop_event` + `finally` seal path | `test_loop_survives_keyboard_interrupt`, `test_loop_interrupt_during_dispatch_stops` |

## Runtime and packaging

| Property | Enforced in | Proven by |
|---|---|---|
| `argus check` probes the same endpoint `run` targets | `api_base_url()` shared by both | `test_api_base_url_shared_by_run_and_check` |
| Wheel ships skills, role prompts, wordlists, exploits, lab | `pyproject.toml` data globs | CI wheel job asserts contents + runs `argus demo` from the installed wheel |
| Demo works offline, no repo checkout needed | `argus/lab/vulnapp.py` packaged; lab seeds into per-run tempdir | `argus demo` on a clean venv (verified on Windows) |
| No runtime deps beyond httpx | `pyproject.toml` | `pip install` footprint |
| Python 3.10 floor honored | stdlib-only usage, no 3.11+ APIs | reviewed + CI |

## Reading order for a first pass

1. `docs/ARCHITECTURE.md` — the layers and why they exist
2. `argus/scope.py` → `argus/httpclient.py` — the boundary everything
   else depends on
3. `argus/session.py` `add_finding` + `seal_artifacts` — the evidence
   contract and the seal
4. `argus/tools/registry.py` `dispatch` — the model/code boundary
5. `argus/team/coordinator.py` — lifecycle: spawn, watchdog, drain, join
6. This file's tables spot-checked against the tests named
