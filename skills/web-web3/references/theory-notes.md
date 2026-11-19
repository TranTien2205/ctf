# Theory notes — the short-form conceptual anchors

## The contract is a state machine

`isSolved()` reads state; the exploit is the transaction that changes it. The
whole class is: which reachable call leaves the predicate's state satisfied.

## Storage is a slot-numbered public map

`private` isn't hidden; a `delegatecall` writes by slot-position; `cast storage`
reads everything. The slot-number is the truth; the var name is a label.

## The call forwards gas and control

`call` runs attacker code in the callee — it can call back (reentrancy) or
`selfdestruct`. The caller doesn't get control back until the callee returns.

## `delegatecall` runs foreign code AS you

The code's `SSTORE N` writes YOUR slot N; `msg.sender`/`msg.value` are the
ORIGINAL ones. The callee's storage layout must match the caller's — a mismatch
is a collision.

## `tx.origin` ≠ `msg.sender`

`tx.origin` is the EOA that started the tx — a contract in the middle makes
them differ. An auth on `tx.origin` is a phish; an auth on `msg.sender` is the
contract.

## A constructor is `extcodesize == 0`

A contract under construction has no deployed code yet — the "is an EOA" check
that reads code-size is bypassed by a constructor call.

## `selfdestruct` is a forced send

`selfdestruct(dest)` sends the balance to `dest` with NO code run — the only
way to force ether into a contract that refuses it.

## `block.*` is public per-block

`timestamp`/`blockhash`/`prevrandao`/etc. are readable — a "random" from them
is reproducible in the same block.

## Arithmetic wraps on <0.8

`0 - 1` → `2**256-1` — the `require` on a wrapped expression passes. `>=0.8`
reverts; `unchecked` re-opens it.

## The transaction is atomic and attributable

Every call/SSTORE/ether-move commits or reverts together — no half-states; and
the `from` is the attributable EOA — the solve is signed and permanent.
