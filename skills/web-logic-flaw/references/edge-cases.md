# Edge cases — the boundary conditions where business-logic shapes break

## Numeric boundaries — the full alphabet

The input parsers disagree about what a number is. Send the whole
alphabet at every numeric field; each row is one probe:

| Value | What it tests |
|---|---|
| `-1` | sign check absent |
| `0` | zero allowed when it shouldn't be (free items, zero-quantity orders) |
| `-0` | signed-zero parser quirk — `Object.is(-0, 0)` is false in JS |
| `0.1`, `0.0000001` | fractional quantities on integer-typed fields |
| `1.0`, `1e0`, `1E0` | float-equals-integer coercion |
| `999999999`, `2147483647`, `2147483648` | int32 boundary — `MAX_INT+1` wraps negative in C-likes |
| `4294967295`, `4294967296` | uint32 wraparound |
| `9007199254740991`, `9007199254740992` | JS `Number.MAX_SAFE_INTEGER` ± 1 — precision loss above |
| `1e308`, `1e309` | float overflow to `Infinity` |
| `Infinity`, `-Infinity`, `inf` | parsers that accept the literal |
| `NaN`, `nan` | `NaN < 10` is false, `NaN > 0` is false — checks "pass" both ways |
| `0x10`, `0o10`, `0b10`, `010` | hex/octal parsing where decimal expected |
| `1,000`, `1 000` | locale/grouped separators |
| `+1`, ` 1`, `1 ` | sign and whitespace coercion |
| `""`, `null`, `[]`, `{}` | empty/null/array/object coercion |
| `true`, `"1"` | boolean and string-typed "numbers" |

Each row needs its own probe and its own response. A `200` on `NaN` that
the total computed as `NaN` — and the order still confirmed — is a
confirmed boundary gap.

## Workflow boundaries

- **Step 0 and step -1**: does the flow accept steps before the first?
- **Step MAX+1**: step past the terminal — does `step=4` on a 3-step flow
  run the terminal action, or wrap?
- **Skipping backward**: complete step 3, then POST step 1 — does state
  rewind?
- **Parallel branches**: a flow with two independent steps — can the
  "optional" branch satisfy a required one?
- **GET on a POST step**: same transition reachable read-only — a CSRF
  or prefetch trigger on a state change.
- **Case variants**: `/Confirm`, `/CONFIRM`, `/confirm/` — routing
  normalization bypassing a per-path state check.

## Replay boundaries

- **Replay across sessions**: redeem code consumed by user A — does user
  B's replay on the same code succeed?
- **Replay across objects**: the idempotency key scoped per-user vs
  per-object vs global.
- **Interleaved replay**: A-B-A-B — does the dedup only compare to the
  immediately previous request?
- **Replay after mutation**: redeem → refund → redeem — does the state
  machine allow re-entry after a compensating action?
- **Time-window replay**: a key that expires — replay after expiry.
- **Replay with mutation**: same idempotency key, different amount —
  first-write-wins or last-write-wins?

## Mass-assignment boundaries

- **Nested objects**: `{"user": {"role": "admin"}}` vs flat `role=admin` —
  the binder may only recurse one level.
- **Array injection**: `role[]=admin`, `role[0]=admin`, `{"role":["admin"]}`.
- **Case variants**: `Role`, `ROLE`, `rOlE` — case-sensitive binders.
- **Dotted paths**: `user.role=admin`, `user[role]=admin` — Rails/PHP
  parameter conventions reaching nested models.
- **Constructor pollution**: `__proto__`, `constructor.prototype.role` —
  the binder that walks the prototype chain (see web-prototype-pollution).
- **Getter-only fields**: a field that binds on write but is computed on
  read — `isAdmin` derived from `role`, so setting `role` indirectly sets it.

## Scaling/transform boundaries (the Pachinko shape)

- `off + id*S` where `off` itself is attacker-influenced.
- `S` negative — index *below* the array base.
- The wrap point: `id` such that `off + id*S ≡ target (mod 2^w)`.
  Compute `id = (target - off) * S^{-1} mod 2^w` when S is odd; for even S,
  solve over the reachable congruence class.
- Signedness: `id` checked as unsigned, arithmetic done signed — `id` in
  `[INT_MAX+1, UINT_MAX]` reads negative on one side.
- Transform applied to `id` in one code path but not another — a second
  accessor on the same structure that skips the check.

## Idempotency boundaries

- **Key reuse across users**: same key, different accounts.
- **Key reuse across endpoints**: `Idempotency-Key` honored on `/redeem`,
  ignored on `/refund`.
- **Partial failure**: first request `500`s after the side effect — does
  the retry double-apply?
- **Header vs body key**: `Idempotency-Key` header plus a `request_id`
  body field — which wins?

## Time boundaries

- `expiry` exactly `now` — inclusive vs exclusive comparison.
- Timezone confusion: `2020-01-01` vs `2020-01-01T00:00:00Z` vs epoch.
- `notBefore` in the future — token valid before its window.
- DST/nonexistent wall times where local-time comparisons run.
