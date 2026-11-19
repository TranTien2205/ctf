# Theory — why the window exists, and what makes it winnable

The underlying model: concurrency, shared state, and a non-atomic
read-then-write.

---

## 1. The TOCTOU definition

**Time-of-check to time-of-use.** The app checks a condition at T1 and acts on
it at T2; between T1 and T2 the condition can change. The check and the use
are not one operation.

```text
T1:  read balance = 100        (the check)
     — the window —
T2:  write balance = 100 - 80  (the use)
     → a second request that read balance=100 in the window also writes -80
```

## 2. Why the check and use separate

They separate because the app's programming model makes them look atomic when
they aren't:

- **The ORM lie**: `obj.field = v; obj.save()` reads like one operation. It is
  a `SELECT` at `find()` and an `UPDATE` at `save()` — the window is the whole
  body between them.
- **The transaction lie**: `BEGIN ... SELECT ... UPDATE ... COMMIT` looks
  atomic. At READ COMMITTED it isn't — the `SELECT` reads a snapshot, the
  `UPDATE` writes a row, and two transactions both do both.
- **The async lie**: `await` looks like a continuation. It is a yield — the
  event loop runs the *other* request right there.
- **The language lie**: "single-threaded Node" is single-threaded only between
  awaits; the awaits are where the other request runs.

## 3. The three ingredients

A race needs all three:

```text
1. SHARED STATE      — a record two requests both touch (a row, a file, a session)
2. A CHECK           — a read whose value decides the act (balance>=x, !used, count<max)
3. A SEPARATED USE   — the write is a different operation than the read
```

Remove any one and the class closes:

- no shared state → no race (per-request data can't conflict)
- no check → no window (a blind insert has nothing to pre-read)
- atomic check+use → no window (one `UPDATE ... WHERE` is the whole thing)

## 4. What makes the window wide

| Widener | Mechanism |
|---|---|
| different functions | read in `get()`, write in `set()` — the call between them is all window |
| external call | email/HTTP/render inside the gap — ms to seconds of width |
| a second query | read A, validate against B, write A — an extra round-trip |
| ORM unit-of-work | read entity, mutate, `commit()` at request end — whole handler is the window |
| work between read and write | logging, notify, transform — every line is width |
| low concurrency ceiling | fewer workers → requests queue → the window is the queue position |
| network latency to the DB | each statement is a round-trip — the gap is the latency |

The single most exploitable: an **external call inside the window** — it's
deterministic, slow, and the attacker controls the input that makes it run.

## 5. Why the naive fix doesn't fix it

```python
# WRONG — a sleep does not close the window
time.sleep(0.01)                      # you still both read pre-state
if balance >= amt: update()

# WRONG — a mutex in app code, but only in one process
lock.acquire(); read(); write(); lock.release()   # two replicas = two locks

# WRONG — a transaction without a lock
BEGIN; SELECT; UPDATE; COMMIT          # READ COMMITTED — both read the snapshot
```

The only closes: an **atomic statement** (check-and-write in one `UPDATE`), a
**lock held from read to commit** (`FOR UPDATE`), a **constraint** that fails
the loser, or **SERIALIZABLE** (the DB aborts one). Everything else narrows the
window without closing it — and a narrow window still loses sometimes.

## 6. The scheduling model — where the other request runs

| Runtime | When the second request runs | Implication |
|---|---|---|
| Node event loop | at every `await` | the window is between awaits |
| Python threads | on any blocking I/O | the second query/send yields |
| Go goroutines | preemptively, anywhere | any point can interleave |
| PHP FPM | truly parallel workers | the gap is the statement boundary |
| Java threads | preemptive | any point; the dirty-flush is at commit |
| the DB | statement-by-statement | the window is the query boundary |

The race is won not by being faster but by **landing in the yield gap** —
which is why the interleave (hold A open, drop B in) beats the burst.

## 7. Attribution — why a flood isn't a win

A race that wins produces a serial-impossible state *attributable to a named
pair*. A flood produces successes without saying which pair crossed — and an
unattributable result is not evidence, it's noise. The proof is "A committed
at T, B inside its window" — name the pair or re-roll.

## 8. The race-vs-logic boundary

A race is a *temporal* bug — the check is correct, the gap is the bug. A logic
flaw is a *spatial* bug — the check itself is wrong, no timing needed.

```text
race:        if (balance>=amt) withdraw();        // check is right; the gap lies
logic flaw:  if (balance>=0) withdraw(-100);      // check is wrong; no timing
```

Same endpoint, different mechanism — classify before probing. The race needs
overlap; the logic flaw works serially.
