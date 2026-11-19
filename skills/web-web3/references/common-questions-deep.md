# Common questions (deep) — the harder cases

## "The setup deploys several contracts — which is the target?"

`isSolved()` reads one — that's the predicate's contract. The others are the
path to it (the token it uses, the library it delegatecalls, the vault it
reads). Map them by which the predicate touches — the rest are the mechanism,
not the target.

## "There's no Setup.sol — just a contract and an address"

The contract IS the challenge — the predicate is whatever the platform reads
(a `solved()`/`flag()`/a state the checker watches). Read the contract's own
`solved`-like getter; if none, the predicate is the flag-state the checker
defines — the contract's docs/comments name it.

## "The only function is guarded — is the challenge unsolvable?"

Enumerate the guard's bypass: `owner` settable? `tx.origin`-based? a sig that's
replayable? a `private` var it reads? a `delegatecall` that writes the guard's
slot? The guard IS the bug surface — `access-control-map.md`.

## "I see `delegatecall` but the layouts look fine — is it safe?"

Check the impl's `SSTORE` map — does ANY impl function write a slot that is
protected in the proxy? A layout "looking fine" needs the per-slot cross-check,
not a glance. `storage-collision-deep.md`.

## "The contract uses `block.timestamp` but the guess needs a specific answer"

Compute the answer in the SAME transaction — a Predict contract calls `guess`
in its own `attack` so the `block.timestamp`/`blockhash` match. Or the answer
is `0`-based (`blockhash(block.number)` is always `0`).

## "The exploit works on the fork but reverts live"

A state assumption differed — a nonce, a block value, an unmocked precompile,
or a state that changed between sim and send. `cast run`/`forge` the failing
tx on the live state; re-read the state at send-time.

## "The contract needs a specific caller I don't have"

Is the caller `tx.origin` (the supplied EOA through a contract), a
`ecrecover`-derived signer (forgeable/replayable), a `private`-var-derived
value (leakable via storage), or genuinely a different key (the challenge
needs that key — check the setup for it)?

## "A challenge with no web3 files but a `.sol` reference"

A web challenge whose flag path goes through a contract — `ctf-web`/`web-*` for
the HTTP surface, this skill for the contract surface. The boundary: the bug
is in the Solidity, so it's `web-web3` for the contract part.

## "How much should I trust `cast call`'s dry-run?"

It simulates the LIVE state at call-time — a block-dependent exploit (randomness)
can differ from the send-time block. For deterministic transitions it's exact;
for block-dependent ones, compute in the same tx.
