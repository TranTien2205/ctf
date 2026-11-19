# Mechanism map — EVM primitive → bug classes it enables

## The call-family map

```
CALL        →  reentrancy (gas-forwarded callback), tx.origin/context confusion
DELEGATECALL→  storage-write / collision / uninitialized-lib / library-kill
STATICCALL  →  read-only-reentrancy (the snapshot oracle), the mid-state read
CALLCODE    →  (legacy delegatecall) — same shape
SELFDESTRUCT→  force-feed / contract-deletion / library-kill
CREATE      →  the lost-address / the contract-EOA trick
CREATE2     →  the predictable-address / the resurrect / pre-computed deploy
```

## The context-op map

```
ORIGIN      →  tx.origin auth — the phish / the contract-in-middle
CALLER      →  msg.sender — the normal check / the contract-in-middle change
CALLVALUE   →  msg.value — a payable path / a value the predicate reads
TIMESTAMP   →  weak-randomness / time-gate
NUMBER      →  weak-randomness / block-gate
BLOCKHASH   →  weak-randomness (or the always-0/current-block trap)
DIFFICULTY  →  (prevrandao) weak-randomness
COINBASE    →  weak-randomness / proposer-dependence
GASPRICE    →  front-running / ordering
GASLIMIT    →  a gas assumption
BALANCE     →  the ether-read — a force-feed target / a balance predicate
SELFBALANCE →  address(this).balance — the drain/force-feed predicate
CODESIZE    →  the contract-EOA check (constructor bypass)
EXTCODESIZE →  the contract-existence check (constructor bypass)
```

## The storage-op map

```
SLOAD       →  reads the predicate's slot / a "private" secret
SSTORE      →  the write — the reachable transition / the collision
SSTORE in a delegatecall → writes the CALLER's slot — the collision
```

## The map's use

Given a bytecode or source, grep the op keywords — each names the primitive and
points at the bug-class file. The `SSTORE`-to-predicate-slot map is the
reachable-transition inventory; the `CALL`/`DELEGATECALL`/`SELFDESTRUCT` ops
name the primitives the exploit can use.
