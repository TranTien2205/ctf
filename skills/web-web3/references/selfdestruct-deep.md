# selfdestruct (deep) — every destruction and force-feed shape

## The exact semantics

`selfdestruct(beneficiary)`:
- erases the contract's code and storage
- sends ALL its ether to `beneficiary` — **with no code run on the beneficiary**
- the beneficiary's `receive`/`fallback`/revert CANNOT refuse the ether

This is the only way to force ether into a contract that rejects it.

## The force-feed shape

```solidity
contract Vault {}   // no receive/fallback — rejects call{value}, .transfer
// isSolved: address(Vault).balance > 0

contract Force {
    constructor() payable {}                       // fund on deploy
    function boom(address t) { selfdestruct(payable(t)); }
}
// Force funded → boom(Vault) → Vault holds ether despite refusing it
```

The force-feed defeats a "contract that must not hold ether" predicate and any
`balance == 0` invariant the challenge assumes.

## The code-deletion shape

`selfdestruct` erases the code — a predicate `extcodesize(addr) == 0` or "the
contract is gone" is solved by it. A `delegatecall`ed library that
`selfdestruct`s destroys the CALLER's context — the parity wallet shape.

## The same-transaction rules (Cancun/EIP-6780)

Post-Cancun, `selfdestruct` only fully deletes code+storage if the contract was
created in the SAME transaction — otherwise it sends the ether but the code
persists. The CTF chain may be pre-Cancun (full delete) or post (ether-only) —
check which behavior the challenge relies on. The force-send works either way;
the code-deletion needs the same-tx rule or a pre-Cancun chain.

## The CREATE2-resurrect shape

A selfdestructed contract's address can be re-deployed via CREATE2 (same
deployer, salt, initcode → same address). A "this address is permanently empty"
assumption breaks — code returns to a "deleted" address. The predicate that
checks `extcodesize` once and caches it is bypassed by a resurrect.

## The library-kill shape (parity)

```solidity
library WalletLibrary {
    function kill() { selfdestruct(owner); }   // callable via delegatecall
}
```

`delegatecall` into `WalletLibrary` → `kill` runs `selfdestruct` on the CALLING
contract's context — destroys the wallet contract. The library's own storage vs
the caller's — see `uninitialized-proxy-deep` for the init+kill chain.

## The force-send to break a `balance` predicate

A contract whose invariant is `balance == X` (not just `> 0`): force-feed to
push it past X, or selfdestruct a CONTRACT THE CHALLENGE DEPLOYED to drain a
balance the predicate reads.

## The evidence

`cast balance $TARGET` shows the forced/drained balance; `cast code $TARGET`
returns `0x` if code was deleted; `isSolved() → true`. The Force/killer
contract's deploy (funded) + the `boom`/`kill` tx + the reads are the chain.
