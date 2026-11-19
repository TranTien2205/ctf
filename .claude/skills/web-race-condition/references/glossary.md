# Glossary — the race-condition vocabulary

The terms this skill uses, each with a one-line meaning and where it's used.

---

## Core terms

| Term | Meaning |
|---|---|
| TOCTOU | time-of-check to time-of-use — the check and the act are separated by a gap |
| window | the gap between the read (check) and the write (commit) — where the race is won |
| check-then-act | the pattern: read a predicate, then act on it |
| read-modify-write | read S, compute S', write S' — the canonical gap |
| crossed state | an outcome impossible under any serial ordering — the proof |
| serial set | the set of outcomes reachable by running the requests one at a time |
| serial baseline | the probe that enumerates the serial set — run before any race |
| max_in_flight | the peak number of requests in flight at once — proves overlap |
| attribution | naming the two requests that crossed — required for evidence |
| falsifier | an observation that closes the class for that endpoint |
| inconclusive | a run that never overlapped — neither win nor negative |
| primitive | what the crossed state buys — money, token, identity |
| the sink | the downstream check the primitive unlocks — where the flag is |

## Delivery terms

| Term | Meaning |
|---|---|
| burst | N complete requests fired at once — for a wide window |
| interleave | request A held open while B completes — for a narrow window |
| last-byte stall | withholding A's final body byte to keep its handler in-flight |
| single-packet | all last bytes/frames in one write — the tightest start barrier |
| barrier | the sync point that releases all primed requests together |
| worker pool | the server's handler capacity — the concurrency ceiling |
| multiplexed | requests sharing one connection — may serialize |

## Database terms

| Term | Meaning |
|---|---|
| READ COMMITTED | each statement reads a fresh snapshot — the default, open |
| REPEATABLE READ | the transaction reads one snapshot — a wider window |
| SERIALIZABLE | the DB aborts a conflicting transaction — closed |
| FOR UPDATE | the read takes a row lock to commit — closed |
| SKIP LOCKED | workers skip rows another transaction holds — queue-safe |
| NOWAIT | fail immediately on a held row rather than block |
| MVCC | multi-version concurrency control — snapshot reads |
| write-skew | two transactions each on a different row violate a joint invariant |
| lost update | two read-compute-writes overwrite each other — a count drops |
| phantom read | a range query's set changes under it via an insert |
| dirty read | a read sees another's uncommitted write |
| optimistic lock | a version column — the loser's update affects 0 rows |
| constraint | `UNIQUE`/`CHECK`/PK enforced at commit — can't be timed out |
| advisory lock | a named app-level lock (`pg_advisory`, `GET_LOCK`) |

## Mechanism terms

| Term | Meaning |
|---|---|
| double-spend | a consumable resource consumed twice |
| token-cross | a secret bound to A delivered to B's channel |
| confused deputy | a privileged actor operating on your (raced) resource |
| stale-read | a view/snapshot read trusted past its validity |
| write skew | the multi-row invariant race |
| lost-update | the blind-overwrite counter race |
| second-order | a crossed state that pays later via a deferred trigger |
| pathological input | a valid-but-slow input that widens the check's window |
| lock expiry | a distributed lock that expires mid-protected-section |
| TOCTOU-on-path | `exists(path)` → `open(path)` — the fs form |

## Tool terms (race_probe.py)

| Flag | Meaning |
|---|---|
| `--url` / `--url-b` | request A / request B (the interleave pair) |
| `--concurrency` | how many in flight — opens that many connections |
| `--count` | total requests to send |
| `--baseline-count` | the serial calibration reps |
| `--no-baseline` | skip the baseline (don't — it's the calibration) |
| `--no-barrier` | send without the primed-release sync |
| `--barrier-timeout` | max wait for all connections to prime |
| `--signature-mode` | how to split win/loss — status/status-length/raw-body/normalized-body/regex |
| `--signature-regex` | the regex for `regex` mode |
| `--signature-header` | the header for header mode (Set-Cookie, Location) |
| `--signature-bytes` | compare only the first N bytes |
| `--reset-url`/`--reset-method`/`--reset-body` | restore starting state between rolls |
| `--write-ack` | acknowledge the blast radius for a write-shaped run |
| `--selftest` | the offline self-test — proves the tool |
| `--challenge`/`--class`/`--hypothesis-id` | the ledger wiring |

## Proof terms

| Term | Meaning |
|---|---|
| confirms | the verdict — a proven serial-impossible outcome |
| evidence | the verbatim excerpt inside `--response` the gate checks |
| negative | a proven-closed layer — a falsifier, recorded |
| kill map | `knowledge/attempts/` — measured-dead layers + reopen-if |
| pre-flag | `hooks.py pre-flag` — the gate a candidate flag must pass |
| family_leads | weak chain-card matches — guidance, never a probe |
| first_confirming_probe | the card's own probe — the one to run |
