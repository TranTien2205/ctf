# Delegatecall (deep) — every shape the primitive takes

## The exact semantics

`target.delegatecall(data)` executes `target`'s CODE but:
- `address(this)` inside the call = the CALLER (storage/context of the caller)
- `msg.sender` = the ORIGINAL caller (preserved, not the delegatecaller)
- `msg.value` = the ORIGINAL value (preserved)
- every `SSTORE`/`SLOAD` hits the CALLER's storage at the callee's declared slots

So `target`'s code runs AS the caller — it can write any caller slot its code
declares, and it sees the original `msg.sender`.

## The three bug shapes

### 1. Attacker-controlled target

```solidity
function run(address impl, bytes data) external {
    impl.delegatecall(data);      // impl is a param → point it at attacker code
}
```

Deploy `Evil { function pwn() { assembly { sstore(0, caller()) } } }`, call
`run(evil, pwn())` — the proxy's slot 0 becomes the caller. **The full control:**
a delegatecall to attacker code writes ANY slot → `owner`, `isSolved` var, or
`selfdestruct` the caller.

### 2. Storage collision (fixed target, wrong layout)

```solidity
// Proxy: slot0=impl, slot1=owner
// Impl:  slot0=a,   slot1=b
impl.setA(x)  →  delegatecall writes PROXY slot 0 → impl = x
```

A mismatch between proxy and impl layouts → an impl function writes a proxy
slot it shouldn't. The proxy's `impl`/`owner` slots are the prize.

### 3. Uninitialized shared library (the parity kill)

```solidity
// WalletLibrary: the impl all wallets delegatecall into
library WalletLibrary {
    function initWallet(address _o) { owner = _o; }   // callable on the lib!
    function kill() { selfdestruct(owner); }
}
```

Call `initWallet` on the LIBRARY → own the library's context → `kill` →
`selfdestruct` destroys the library (and any contract whose `delegatecall`
context it was). The storage is the CALLER's — the library's own storage is
what the direct call writes.

## The delegatecall chain shape

```
caller EOA --calls--> proxy --delegatecall--> impl
impl's code writes PROXY's storage; msg.sender = caller EOA
```

For a stored-`owner` overwrite: `impl.setOwner(addr)` delegatecalled writes
PROXY's `owner` slot (if the slots align) → `owner = msg.sender = caller`.

## The detection (bytecode)

- a `DELEGATECALL` op — the contract delegates somewhere
- read the target: `cast storage` the slot the `DELEGATECALL`'s address comes
  from (the impl/library slot)
- the impl's `SSTORE` map → which proxy slots the impl's functions write

## The variants

| Variant | The shape |
|---|---|
| a settable impl | `setImpl(addr)` → point it at attacker code |
| a collision | impl writes a proxy slot it shouldn't |
| an uninitialized lib | `initWallet`/`init` on the shared code |
| a selfdestruct-in-lib | `kill` in the delegatecall'd code destroys the caller |
| the `PuzzleWallet` shape | a proxy + wallet where `multicall`/`deposit` through the delegatecall double-counts |
| the `Preservation` shape | `setFirstTime`/`setSecondTime` write the same slot → overwrite `owner` |

## The evidence

`cast storage $PROXY <slot>` before/after — the write landed where intended;
`isSolved() → true`. The delegatecall's tx + the slot read are the chain.
