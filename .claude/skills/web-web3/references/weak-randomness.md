# Weak randomness / predictability — read the source the contract reads

## The shape

```solidity
function guess(uint _g) public {
    uint answer = uint(keccak256(abi.encode(blockhash(block.number-1), block.timestamp)));
    if (_g == answer) { solved = true; }
}
```

The "random" is a public-chain value: `block.timestamp`, `block.number`,
`blockhash`, `block.difficulty`/`prevrandao`, `block.coinbase`, or a
`keccak` of public state. A contract that reads the same source computes the
same answer — the caller predicts it.

## The detection fingerprint

- `block.timestamp`/`blockhash`/`block.number`/`prevrandao`/`difficulty`/`coinbase`
  feeding a decision
- a `keccak`/`sha` of public state used as a secret
- `private` storage read as a secret (it isn't — `cast storage` reads it)
- **falsifier**: a real VRF/commit-reveal, or the decision doesn't read
  predictable state

## The exploit

```solidity
contract Predict {
    function attack(address t) external {
        uint answer = uint(keccak256(abi.encode(blockhash(block.number-1), block.timestamp)));
        Target(t).guess(answer);   // SAME block → same timestamp/blockhash → same answer
    }
}
```

Compute the "random" in the SAME transaction/block — the values match
deterministically. For a seed in `private` storage, read it with
`cast storage` and submit the answer directly.

## The per-source table

| Source | Predictability |
|---|---|
| `block.timestamp` | same-block → identical; a validator skews it a few seconds |
| `blockhash(n)` | public; only for `n` in the last 256 blocks, else `0` |
| `block.number` | public, deterministic |
| `block.prevrandao`/`difficulty` | the beacon's randao — public per-block |
| `block.coinbase` | the block proposer — public |
| `keccak(public-state)` | reproducible — not a secret |
| `private`/`internal` var | readable via `cast storage` — not a secret |
| `blockhash(block.number)` | ALWAYS `0` (current block has no hash yet) — a contract that uses it computes on `0` |

## The commit-reveal boundary

A `commit(hash) → reveal` scheme is the FIX, not the bug — the hash hides the
value until committed. The bug is only a scheme that reads a
same-block-predictable source. A future-block `blockhash` is predictable the
moment that block lands.

## The evidence

`isSolved() → true` after the `Predict.attack` tx; the contract's stored
answer matches the computed one. The Predict contract's deploy + attack tx are
the chain.
