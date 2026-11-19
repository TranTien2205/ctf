# Timing oracle — the hash-asymmetry channel

## The physics

`verify(password, hash)` for a memory-hard/KDF hash is deliberately
slow — that is the point of bcrypt, argon2, scrypt, PBKDF2. The
`user is None` arm skips it. The delta is the whole oracle:

| Hash | Typical cost | Oracle strength |
|---|---|---|
| bcrypt cost 10 | ~60-100ms | strong |
| bcrypt cost 12 | ~250ms | strong |
| argon2id | ~100-500ms | strong |
| scrypt | ~50-200ms | strong |
| PBKDF2 600k iter | ~100-300ms | strong |
| PBKDF2 50k iter | ~10-40ms | moderate |
| sha256/md5/sha1 | <1ms | **weak — sub-jitter** |
| plaintext/no hash | ~0ms | none — no work asymmetry |

A weak-hash app gives a weak timing oracle — the delta is real but
swamped; fall back to a content channel.

## The measurement protocol

```bash
# alternate good/bad to cancel drift; interleave, don't batch
> t.txt; for i in $(seq 12); do
  curl -s -o /dev/null -w "good %{time_total}\n" -X POST -d 'user=KNOWN&pass=x' "$BASE/login" >> t.txt
  curl -s -o /dev/null -w "bad %{time_total}\n" -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" >> t.txt
done
awk '$1=="good"{g+=$2;ng++} $1=="bad"{b+=$2;nb++} END{print "good_med",g/ng,"bad_med",b/nb,"delta",g/ng-b/nb}' t.txt
```

- **N >= 8-12** per arm — one shot is noise
- **interleave** good/bad — a batch-good-then-bad order confounds drift
- **median**, not mean — one 3s outlier skews a mean
- **same session/connection** where possible — load balancers route
  different workers; a keep-alive session or a cookie pins affinity
- **control for the network** — run a baseline of two random strings to
  measure the transport jitter; the signal is the good-vs-bad delta
  ABOVE that jitter

## The significance test

```
delta = median(good) - median(bad)
jitter = stdev(pooled medians of random-vs-random pairs)
signal = delta > ~3 * jitter  (and repeats on a re-run)
```

A delta that survives a second run with a DIFFERENT bad name is a real
oracle — it tracks the username, not the one bad string.

## Timing-equalized defenses — the artifact hunt

A competent defense burns a dummy hash on the bad arm:

```python
if not user:
    hash_password(password)   # burn time to match
```

Then timing is equal — hunt the OTHER channels: a `Set-Cookie`, a
different template branch, a cache write, an audit log, a subtle body
byte. The equalization is itself detectable — the bad arm's timing has
less variance (one fixed hash) than the good arm's (real per-user hash
may vary with stored cost).

## The remote-target caveat

On a remote target, network jitter (~10-50ms RTT variance) swallows a
sub-10ms delta. Mitigations: more samples, a local baseline, measuring
server-side `Date`/response-time if exposed, or dropping to a content
channel. Never claim a timing oracle from a delta within the noise floor.
