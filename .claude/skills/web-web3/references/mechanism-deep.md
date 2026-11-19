# Mechanism (deep) — the EVM execution model a web3 exploit exploits

## The transaction lifecycle

```
EOA signs tx --> mempool --> included in a block --> EVM executes --> state
```

A transaction carries `from`, `to`, `value`, `data`, `gasLimit`, `gasPrice`,
`nonce`. Executing it runs the `to` contract's code; each `call`/`delegatecall`/
`staticcall`/`create` inside spawns a sub-call with its own context. The state
changes (SSTORE, balance moves) commit only if the whole transaction succeeds —
a revert rolls back EVERYTHING including the sub-calls.

## The context tuple

Every call frame carries:

```
msg.sender    the immediate caller (EOA or contract)
msg.value     the ether forwarded to THIS call
msg.data      the calldata — selector + encoded args
tx.origin     the EOA that started the whole transaction (never changes)
address(this) the contract whose storage THIS frame reads/writes
```

`call` → new frame, `this` = callee, `sender` = caller.
`delegatecall` → new frame, `this` = CALLER's storage, `sender`/`value` preserved.
`staticcall` → new frame, no state writes allowed.

## The storage model in detail

Storage is a `bytes32 → bytes32` map keyed by slot. Layout rules:

```
scalar vars declared in order → slots 0, 1, 2, ...
vars < 32 bytes pack right-to-left into one slot
mapping(k => v) at slot p     → v at keccak256(h(k) . p)
dynamic array at slot p       → length at p, elem[i] at keccak256(p) + i
bytes/string at slot p        → len<=31: data+len in p; len>=32: len*2+1 at p,
                                data at keccak256(p) + i
struct declared at slot p     → its members fill p, p+1, ...
```

A `delegatecall` runs foreign code on THESE slots — the callee's `SSTORE N`
writes the caller's slot N, whatever the var name. This is the whole
delegatecall/storage-collision bug family.

## The call-frame security boundary

- a `call` forwards gas and runs the callee — the callee's `fallback`/`receive`
  is arbitrary code → **reentrancy**: it calls back before the caller settles
- a `delegatecall`'s code is trusted implicitly — it writes your storage →
  **delegatecall/storage-collision**
- `tx.origin`/`msg.sender` split → **the phish**: a contract in the middle
- `extcodesize` on a constructor → **the EOA trick**: code-size 0 mid-deploy

## The ether model

A contract's ether moves only via: a payable call-in, `selfdestruct` (forced),
or being the block's `coinbase`. There is NO way to refuse a `selfdestruct`'s
ether — this is the force-feed primitive. `.transfer`/`.send` cap the gas at
2300 (no reentrancy room); `call{value}` forwards all gas (reentrancy room).

## The block context

`block.timestamp`, `block.number`, `blockhash(n)`, `block.coinbase`,
`block.difficulty`/`prevrandao`, `block.basefee`, `tx.gasprice`, `gasleft()` —
all public, all deterministic per-block (except `blockhash` which is `0` for the
current and >256-old blocks). A contract that uses these for a "secret" or a
decision is **weak-randomness** — the caller reads the same values in the same
block.

## The precompile surface

`ecrecover` (addr 1), `sha256` (2), `ripemd160` (3), `identity` (4), `modexp` (5),
`ecadd`/`ecmul`/`ecpairing` (6-8), `blake2f` (9). `ecrecover` returns `address(0)`
on a bad sig — the signature class. `ecpairing` is the ZK-SNARK surface.

## The revert/commit rule

`revert`/`require`/`assert` rolls back ALL state changes in the transaction —
including sub-calls and ether moves — but the GAS is still spent. A failed
exploit costs gas but changes nothing. This is why the dry-run/fork is where
iteration lives: a sim-revert costs nothing; a live-revert costs gas.

## The solved-predicate mechanism

`isSolved()` is a `view` call — it reads state, changes nothing. The checker
calls it (or a `solve()` that checks it). The exploit is the sequence of
`cast send`s (or one attack-contract `run()`) that leaves the predicate's
slots/reads in the solved state. The whole class reduces to: **which reachable
transition leaves the predicate's storage reads true?**
