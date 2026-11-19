# Front-running (deep) — ordering and atomicity in full

## The mempool visibility

A pending transaction sits in the mempool — its calldata is visible before it
lands. A contract that rewards the FIRST correct caller lets a mempool-watcher
copy the answer and submit it first with a higher gas price. In a private CTF
chain the "watcher" is the supplied caller's own bot — or the ordering
dependency is in the contract logic, not the mempool.

## The ordering-dependency shape

The more common CTF shape: a function's result depends on CALL ORDER, and the
exploit is a contract that forces a specific order atomically:

```solidity
// the contract assumes a normal order — the exploit forces a different one
contract Solver {
    function run() external {
        t.step1();
        t.step2();   // lands in the SAME tx — guaranteed order
    }
}
```

An atomic `run()` guarantees the sequence — a two-call exploit the author
assumed couldn't be atomic.

## The ordering bug classes

| Shape | The exploit |
|---|---|
| **first-come/claim** | copy the answer, submit first (higher gas) — or a contract that claims atomically |
| **a commit-then-act leak** | the first step reveals data the second uses — a contract reads it and calls the second in one tx |
| **a check-then-act window** | `check()` then `act()` as separate calls — a contract does them in one atomic tx, or interleaves |
| **a price/auction** | the bid/order that lands first wins — the atomic sequencer |
| **a TOCTOU between two contracts** | contract A checks contract B's state, then acts — a contract that changes B between the check and act in one tx |

## The commit-reveal boundary

`commit(hash) → reveal` hides the value until after the commit window — the
ordering-leak fix. A challenge that uses a plain `answer`/`action` param is
exploitable; a real commit-reveal isn't.

## The same-atomicity rule

The ordering exploit is reliable because a contract's `run()` is atomic — the
steps can't be interleaved with a third party's tx. A sequence of separate
`cast send`s could be front-run itself — prefer one atomic contract call when
ordering matters.

## The detection fingerprint

- a `winner`/`first`/`claim`/auction/first-come decision
- a two-step (commit→act, check→act) whose steps a contract could atomize
- a decision that reads an orderable/mempool-visible value
- **falsifier**: commit-reveal, or the decision isn't ordering-sensitive

## The evidence

`isSolved() → true` after the ordering-forcing tx; the receipt's `logs` show
the calls landed in the needed order (an atomic contract tx guarantees it).
