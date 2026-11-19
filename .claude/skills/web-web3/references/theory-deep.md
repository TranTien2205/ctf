# Theory (deep) — why the web3 bug classes exist

## The trust-inversion root

A web app trusts the server and the request is ephemeral. A smart contract is
the OPPOSITE: the code is immutable and public, the state is a public ledger,
and every caller is untrusted-by-default. The bugs are the places the contract
assumes a trust that doesn't exist:

- it assumes a `private` var is hidden — it's on a public ledger
- it assumes `tx.origin` identifies the user — a contract sits in the middle
- it assumes a `call` returns control — the callee is arbitrary code
- it assumes the code it `delegatecall`s is trusted — the target is influenceable
- it assumes `block.*` is unpredictable — it's public per-block
- it assumes arithmetic stays in range — pre-0.8 it wraps
- it assumes a storage var's name protects it — the slot is a number

## The shared-everything root

Unlike a web app's per-request isolation, EVERYTHING a contract does is shared:
the storage is a public map, the code is public, the call history is public. A
contract that hides a secret or assumes a private state is broken by design —
the only real secret is a key never sent on-chain.

## The atomicity root

A transaction is atomic — every call, SSTORE, and ether-move inside it commits
or reverts together. This makes some bugs impossible (a half-completed transfer
can't persist) and enables others (a flash-loan's borrow-use-repay in one tx,
an atomic multi-step exploit). The atomicity is why the ordering-sensitive bugs
are exploitable at all — a contract can't see a mid-tx state from outside, but
a contract CAN sequence the whole exploit inside one tx.

## The immutability root

Deployed code can't change — a bug is permanent (the force-feed, the
unprotected setter). A proxy/delegatecall is the workaround — and the
delegatecall is its own bug family. The immutability is why `selfdestruct` and
the uninitialized-init exist: the only ways to "change" deployed behavior are
destructive or delegate-based.

## The attribution root

Every transaction is attributable to an EOA — `tx.origin`/`msg.sender`. The
solve must be a transaction from the supplied caller (or a contract it
deployed). There's no anonymous solve — the receipt is the proof and the
attribution.

## The "the contract is the server" root

There's no hidden server-side state — `cast storage` reads everything, `cast
code` reads the logic. The challenge is entirely about REACHABILITY: which
transaction can the supplied caller send that leaves the predicate's state
satisfied. The bug classes are the reachable state-changes the author didn't
intend to allow.

## The catalogue-honest note

This class is `catalogue` — the corpus is published knowledge of these root
causes, not locally verified solves. A real solve's `../field-notes.md` entry is
what moves it to `verified`.
