# Timing statistics — the measurement, rigorously

## Why one request is never a verdict

Network jitter on a remote target is 10-50ms; server queueing adds more.
A single `curl -w '%{time_total}'` reading 240ms on `admin` and 220ms on
`zzz` is INSIDE the noise — the delta is unmeasurable at N=1. The whole
timing channel is a statistical claim, not a single observation.

## The sampling protocol

```bash
> t; for i in $(seq 16); do
  # interleave — alternate good/bad so drift affects both arms equally
  curl -sb $cj -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)&_=$i" "$FORM" >> t
  curl -sb $cj -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x&csrf=$(tok)&_=$i"  "$FORM" >> t
done
```

Interleaving is the control — if the server warms up, slows down, or a
balancer shifts, both arms see it; a non-interleaved run attributes the
drift to the username.

## The statistics — medians, not means

```bash
# median per arm + the jitter baseline (bad-vs-bad spread)
python3 - <<'PY'
import statistics as s
g=sorted(float(l.split()[1]) for l in open('t') if l.startswith('g '))
b=sorted(float(l.split()[1]) for l in open('t') if l.startswith('b '))
def med(x): return s.median(x)
print('good med %.3f  stdev %.3f' % (med(g), s.stdev(g)))
print('bad  med %.3f  stdev %.3f' % (med(b), s.stdev(b)))
# jitter = the spread on the bad arm itself
jit = s.stdev(b)
delta = med(g)-med(b)
print('delta %.3f  = %.1fx jitter' % (delta, delta/jit if jit else 0))
PY
```

- median, not mean — a mean is skewed by a single slow outlier
- `delta / jitter` — the signal-to-noise; `> 3x` is a real gap, `< 1.5x`
  is noise
- the bad-vs-bad2 spread is the baseline jitter, not the good-bad diff

## The verdict table

| `delta/jitter` | Verdict |
|---|---|
| `> 3x` | a real oracle — the verify-short-circuit |
| `1.5-3x` | marginal — increase N, re-run, re-measure |
| `< 1.5x` | noise — not an oracle |
| `delta ≈ 0` | equalized (a dummy-hash) or a fast hash |

## The expected gap by hash

| Hash | Typical cost | Expected gap |
|---|---|---|
| MD5/SHA-1/SHA-256 | ~0.001ms | sub-jitter — unmeasurable |
| SHA-512 | ~0.01ms | sub-jitter |
| PBKDF2 10k | ~5-10ms | marginal — needs the baseline |
| PBKDF2 100k+ | ~50-100ms | measurable |
| bcrypt cost 10-12 | ~80-300ms | easy |
| argon2id | ~100-500ms | easy |
| scrypt | ~50-200ms | easy |

A fast-hash app (MD5/SHA) is NOT a "no-timing" — it is an unmeasurable
timing; the gap exists but is below the jitter floor. Drop to the
content channels.

## The variance channel — a subtler signal

A time-EQUALIZED app hashes a DUMMY on the miss. A fixed dummy has a
constant cost → LOWER stdev on the bad arm than the per-user real-hash
stdev on the good arm:

```bash
# stdev(good) vs stdev(bad) — a real-user hash varies; a dummy is constant
```

`stdev(good) > stdev(bad)` on an equalized-mean app → the defense is a
fixed dummy → still a differential (the variance leaks it).

## The affinity caveat — pin the session

Behind a balancer, different workers have different load → a bimodal
distribution that masquerades as a gap. Pin `KNOWN` and `FAKE` to the
SAME session/worker (same cookie jar, or a sticky `X-Forwarded-For`),
or the bimodality is a worker effect, not the username.

## The re-run rule

A timing verdict requires the delta to REPEAT on a second run. A single
run's delta could be a transient — re-run the interleaved set; the gap
must survive. `delta > 3x jitter` on TWO independent runs is the
confirmation.

## Recording the timing verdict

```
form: POST /api/login    channel: timing
N=16 interleaved   good_med=0.247  bad_med=0.009  jitter=0.005
delta=0.238 = 47x jitter   (repeated on re-run)
verdict: oracle — the verify-short-circuit (a KDF-cost gap)
```

Never "it seemed slower" — the N, the medians, the jitter, the ratio.
