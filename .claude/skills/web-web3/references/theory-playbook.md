# Theory playbook — applying the root causes to a live challenge

## Step 1 — identify the contract's trust assumptions

Read the contract and name what it ASSUMES that isn't true:

```text
"it assumes this var is hidden"           → visibility
"it assumes this caller is the user"      → tx.origin / the contract-in-middle
"it assumes the call returns control"     → reentrancy
"it assumes the delegatecall'd code is trusted" → delegatecall
"it assumes the arithmetic stays in range" → integer-overflow
"it assumes block.* is unpredictable"      → weak-randomness
"it assumes it can refuse ether"           → selfdestruct force-feed
"it assumes a signature is single-use"     → signature-replay
"it assumes the tracked sum equals real"   → accounting-vault
"it assumes the proxy/impl share context"  → uninitialized-proxy
```

The assumptions ARE the bug surface — each is a falsifiable trust the contract
extends.

## Step 2 — the predicate picks the assumption

`isSolved()`'s expression names which assumption the challenge exercises:

```
owner() → the caller-identity assumption
balance → the state/callback assumption
flag    → the write-access assumption
answer  → the entropy/secret assumption
```

## Step 3 — the reachable surface the assumption lives on

The assumption is only exploitable where a reachable function exercises it —
the inventory of non-view external/public functions that touch the predicate's
slots is where the assumption's falsifiability is tested.

## Step 4 — the mechanism the assumption needs

Each assumption maps to a primitive — `delegatecall` for storage-trust, `call`
for the callback, `block.*` for entropy. The contract must USE the primitive for
the assumption to be a bug — a `tx.origin` assumption is only exploitable if a
reachable function checks `tx.origin`.

## Step 5 — the transition the assumption enables

The falsified assumption is a reachable transition the author didn't intend —
the bug. The exploit is the transaction that exercises it; `isSolved()` flips
because the assumption let the transition change the protected state.

## The theory's practical use

The theory isn't decoration — it's the falsifier-generator. Each "the contract
assumes X" is a hypothesis the cheapest probe can test. The catalogue of root
causes (`theory-catalogue.md`) is the enumeration of what a contract CAN'T
assume — the detection reads the contract for each.
