# Per-surface map — the interaction surface → the check

## The surface inventory

| Surface | The check |
|---|---|
| the `Setup.sol` | `isSolved()` — the predicate; the deployed `challenge`/`player` addresses |
| the `Challenge.sol` | the reachable functions — which write the predicate's slots |
| the deployed bytecode | `cast code` — does it match the `.sol`? decompile if not |
| the storage | `cast storage` the predicate's + the writable slots |
| the RPC endpoint | `cast chain-id`, `cast block-number` — the live private chain |
| the supplied private key | the attributable caller — `cast wallet address --private-key $KEY` |
| the deploy/receipt logs | `cast tx`, `cast logs` — constructor args, emitted secrets |
| a front-end/ABI if shipped | the intended functions — the callable surface |

## The read-only surface pass

Before any write, enumerate:

```bash
cast call $SETUP "isSolved()(bool)"
cast call $SETUP "challenge()(address)"  # or whatever the setup exposes
cast code $CH --rpc-url $RPC             # the real bytecode
for s in 0 1 2 3 4; do cast storage $CH $s; done   # the low slots
cast balance $CH
```

## The write surface

The reachable non-view `external`/`public` functions — the only places a
transaction can change state. Enumerate them from the source or the bytecode's
dispatch table; each that touches the predicate's slots is a candidate.

## The chain-surface

The supplied caller can deploy contracts — the attack surface includes any
contract the caller deploys (a `Phish`, a `Predict`, a `Force`, a `Solver`).
The chain isn't just the challenge's functions; it's the caller's deployed
contracts calling them.

## The per-instance surface

RPC URL, key, addresses — all per-instance. The surface check first confirms
the live instance: `cast chain-id`, `cast block-number`, the setup's
`isSolved()` reading `false` (a `true` on a fresh instance means a stale
reading or a trivially-solved setup).
