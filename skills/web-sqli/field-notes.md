# Field notes — SQL injection

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## 2026-09-07 · red-island-2 · proposed

- source note: `solved/red-island-2.md`
- chain card: `knowledge/chains/htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli.json`
- verification: verified_live — extracted value confirmed by a HEX equality probe
- classified as: `web-sqli` (score 5.5, 5 signals matched)
- also matched: `web-race-condition` (1.5), `web-cache-poisoning` (1.0)
- signals that fired: ORDER BY, SELECT note FROM notes WHERE assignee = '%s'`.
2. WAF (on RA, SQL, mysql, time-based

**Confirming probe that worked**

> send one blocked keyword as unicode escapes and compare the response with the same keyword sent literally

Expected: the escaped form is accepted while the literal form is rejected

Falsifier: both forms are rejected, so the filter runs after decoding

**Traps recorded on this solve**

- grouped concatenation needs an explicit ordering or rows arrive in a different order each query
- parallel timing probes contend on the worker pool and corrupt the oracle; extract sequentially
- measure the baseline before choosing a threshold; jitter can cross a threshold set too close
- end of string reads as a space in a numeric binary search; test for a non-zero character code before appending
- compare hex strings as strings, not as a numeric literal, or the comparison silently fails

**Blast radius**: conditional sleeps hold a worker per matching row; keep the row count and the sleep short on a shared instance

- status: proposed

## 2026-09-23 · Expense Tracker · proposed

- source note: `solved/picoctf-expense-tracker-second-order-sqli.md`
- chain card: `knowledge/chains/picoctf-expense-tracker-second-order-sqli-async-report-union.json`
- verification: verified_live — the flag was read from the artifact downloaded from the live target, as the value of a row returned by the injected union
- classified as: `web-sqli` (score 3.5, 3 signals matched)
- also matched: `web-ssrf` (1.5), `web-logic-flaw` (1.0), `web-idor` (1.0)
- signals that fired: sql, sqlite, union select

**Confirming probe that worked**

> create two accounts differing only in that one chosen value ends with a single quote, trigger the deferred action for both, and read where each result is reported

Expected: the plain account produces its artifact while the quoted one reports a database parse failure, naming the doubled quote

Falsifier: both accounts produce their artifact normally, so the stored value is parameterised in the worker too

**Traps recorded on this solve**

- the insert is parameterised and accepts the payload silently, so testing the request that stores the value shows nothing and the flow looks safe
- the table whose name decodes to a claim that no flag is present is exactly where the flag was, so enumerate it rather than trusting the label
- the worker's failure reason is rendered back to the attacker, which makes this error-based rather than blind; look for that text before building a boolean oracle
- the chosen value is also used to build the artifact filename, so a payload containing a path separator breaks file creation instead of reaching the query
- omitting a required registration field returns a bare bad-request page with no field named, which reads like a broken request rather than a missing input

**Blast radius**: read-only. Each payload costs one throwaway account plus one record, and the deferred job only reads. The chosen value is uniqueness-checked, so every payload needs a distinct prefix rather than a retry of the same one. Avoid a path separator in the payload: the value is also used to build the artifact's filename, so a separator breaks file creation instead of reaching the query.

- status: proposed

## 2026-09-23 · crystal-peak · proposed

- source note: `solved/pico-crystal-peak-second-order-sqli-async-report.md`
- chain card: `knowledge/chains/pico-crystal-peak-second-order-sqli-async-report.json`
- verification: verified_live — An account named "v7' UNION SELECT name||'='||value,42,1 FROM aDNyM19uMF9mMTRn-- " produced the report file report_v7'...csv whose CSV body was flag=picoCTF{...},42,1. The constant 42 was chosen as a marker so the row is provably from this injection rather than from another player's artifact visible through the same instance's missing ownership check.
- classified as: `web-sqli` (score 3.5, 3 signals matched)
- also matched: `web-auth-session` (3.5), `file-read-primitives` (3.5), `web-ssti` (2.5)
- signals that fired: SQL, UNION SELECT, sqlite

**Confirming probe that worked**

> Register an account whose name contains a single quote plus a UNION selecting constants, with as many terms as the generated artifact has columns, then trigger the job and read the artifact.

Expected: The artifact contains an extra row made of your constants, proving the stored name was interpolated into the query rather than bound as a parameter.

Falsifier: The artifact contains only real rows, or the job reports an error that names the stored value as data. The query is then parameterised and this class does not apply; look for the injection where the value is consumed rather than where it is stored.

**Traps recorded on this solve**

- Testing the input only at submission time proves nothing about a second-order bug. Every direct probe of the username here returned a normal page while the injection already worked in the deferred job.
- Choose an oracle the bug can actually speak through. HTTP status and response length cannot see a query whose only output is a file generated ten seconds later.
- A size-filtered parameter fuzz cannot find an ORDER BY parameter, because sorting changes row order and not response length. Compare the sequence of marker rows instead.
- An obfuscated table name may be encoded rather than random; decoding it is free and here it read 'h3r3_n0_f14g', which was a joke and not a reason to skip the table.
- On a shared instance another player's artifacts may already contain the answer. Treat that as a lead only, and reproduce it with a marker of your own before recording it.

**Blast radius**: Low but not zero. Reading is harmless, but the injection runs inside a job with database access, so keep every payload to SELECT and never append a second statement. Each attempt also creates a durable account and artifact rows that other players can see, so use distinctive throwaway names and do not delete or modify rows that are not yours. On a shared instance, other players' artifacts are readable through the missing ownership check; read them for orientation but do not disturb them.

- status: proposed

