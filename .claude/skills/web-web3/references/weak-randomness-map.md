# Weak-randomness map — the predictable-source shapes indexed

## The source → the predictability → the exploit

| Source | Predictability | The exploit |
|---|---|---|
| `block.timestamp` | same-block identical | a Predict contract in the same tx |
| `block.number` | public, deterministic | compute the answer directly |
| `blockhash(n)` | public; `0` for current/`>256`-old | the same-block compute, or the `0`-based answer |
| `block.prevrandao`/`difficulty` | public per-block | the same-block compute |
| `block.coinbase` | the proposer | public — compute it |
| `block.basefee` | EIP-1559, public | compute it |
| `tx.gasprice` | the caller picks it | the caller's own value |
| `keccak256(public)` | reproducible | compute it |
| `private`/`internal` var | readable | `cast storage` it |
| `address(this).balance`/`extcodesize` | public chain state | read it |

## The answer-shape → the call

| The answer | The call |
|---|---|
| `uint(keccak256(...))` | compute the same hash in the same tx → `guess(a)` |
| `blockhash(block.number-1)` | read it — or `0` if the block is current |
| a `private` seed | `cast storage` it → `guess(the-leaked-answer)` |
| a `bytes32` the contract hashed | brute a small space — `keccak("rock")` |

## The same-block-vs-later-block split

| The shape | The exploit |
|---|---|
| the answer computed and used in the same call | the Predict contract computes it in the SAME tx — the values match |
| the answer committed in block N, used in N+1 | compute it in N+1 — the block's values are known |
| the answer from `blockhash(block.number)` | ALWAYS `0` — compute the `0`-based answer |
| the answer from a `private` seed | `cast storage` the seed — compute offline, submit |

## The falsifier map

| The falsifier | Closes |
|---|---|
| a commit-reveal (hash the value until after) | the same-block read — the value is hidden at commit-time |
| a real VRF (a verifiable random function) | the predict — the VRF's output isn't reproducible |
| the decision doesn't read `block.*`/readable state | weak-randomness — the source isn't there |

## The exploit-contract template

```solidity
contract Predict {
    function attack(address t) external {
        uint a = /* the same computation the contract does, the same block */;
        ITarget(t).guess(a);
    }
}
```

`weak-randomness.md`/`weak-randomness-deep.md` for the full shapes.
