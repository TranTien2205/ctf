# State replay deep — the dedup internals and the replay algebra

`state-replay.md` covers the probe. This module is the dedup machinery —
where consumed-markers live, what they cover, and the full replay
algebra.

## The dedup implementations

```js
// 1. no marker — the pure bug
const c = await Code.findOne({code});
user.balance += c.value; await user.save();
// nothing marks c consumed

// 2. late marker — check-then-set
if (c.used) return 409;
user.balance += c.value; await user.save();
c.used = true; await c.save();          // ← window between find & set

// 3. atomic marker — the fix
const c = await Code.findOneAndUpdate({code, used:false}, {used:true});
if (!c) return 409;
user.balance += c.value;
```

Shape 1 replays serially. Shape 2 falsifies serially but races in
parallel — the serial `409` is the class boundary: dead for logic,
alive for `web-race-condition`. Shape 3 is the real fix.

## The key-coverage taxonomy

A dedup marker answers "consumed" against a KEY. The key's scope is the
mechanism's real boundary:

| Key shape | Replay that still works |
|---|---|
| `(code)` | none — global dedup |
| `(user, code)` | cross-user: B replays A's code |
| `(requestId)` | same action, new requestId |
| `(endpoint)` | same action via `/claim` vs `/redeem` |
| `(user, code, day)` | replay on another day |
| `(body-hash)` | mutated body + same key → first-write-wins? |

Probe order for a `409`: same-key-mutated-body → cross-user →
cross-endpoint → cross-time — each is one curl with the coverage
question attached.

## The replay algebra

| Replay | Tests |
|---|---|
| `A,A` serial | marker exists? |
| `A,A,A,...` | count cap vs binary marker |
| `A,B,A` interleaved | dedup compares only to previous? |
| `A(key=k), A'(key=k, body mutated)` | first-write-wins |
| `A(user1), A(user2)` | cross-user scope |
| `A(obj1), A(obj2)` | per-object vs global |
| `A → refund → A` | re-entry after compensation |
| `A(t), A(t+window)` | expiry-window replay |
| `GET A`, `POST A` | method-bound dedup |
| `A` ×N parallel | the TOCTOU window (race) |

## The evidence shape

The replay confirm is a diff series:

```
before:  {"balance": 100}
after1:  {"balance": 150}     ← first application
after2:  {"balance": 200}     ← the replay applied again
```

Three reads, verbatim — the mid-read (`after1`) is what makes `after2`
attributable to the second POST rather than drift.

## Replays that aren't codes

- **password-reset tokens**: single-use tokens consumed on use — replay
  the same link.
- **OAuth/invite codes**: consumed on redemption — cross-user replays
  matter (invite consumed by A, replayed by B).
- **votes/likes**: per-user markers — cross-session replay.
- **idempotency-key'd writes**: `Idempotency-Key` header stores — same
  key mutated body.
- **webhook deliveries**: event IDs dedup'd — redeliver the same event.

## The serial/parallel boundary

The rule that keeps this class honest: SERIAL probes are logic-flaw's;
PARALLEL windows are `web-race-condition`'s. A `409` on serial replay
ends this class's question on that endpoint — the parallel probe goes
to `race_probe` with `--write-ack`, serial baseline first.
