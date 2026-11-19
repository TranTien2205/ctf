# Delegatecall — foreign code writes your contract's storage

## The shape

```solidity
contract Proxy {
    address public implementation;          // slot 0
    fallback() external {
        implementation.delegatecall(msg.data);   // runs impl code on MY storage
    }
}
```

`delegatecall` runs the target's code **in the caller's storage and context** —
`msg.sender`/`msg.value` preserved, but every `SSTORE` lands on the CALLER's
slots at the positions the implementation's code declares. Two bugs fall out:

1. **delegatecall to an attacker-controlled address** → the attacker's code
   writes the contract's storage → overwrite `owner`, flip a flag, `selfdestruct`.
2. **storage-collision** → the implementation's declared layout doesn't match
   the proxy's, so a write meant for impl's slot lands on the proxy's `owner`.

## The detection fingerprint

- a `delegatecall` whose target is a parameter, a settable var, or a
  library address the caller can influence
- a proxy pattern (`fallback` → `delegatecall(implementation)`)
- a `WalletLibrary`/shared-library shape — `delegatecall` into code with an
  unprotected `init`/`kill`
- **falsifier**: `delegatecall` target hardcoded and storage layouts verified
  matching, or no `delegatecall` at all

## The exploit shapes

### Take ownership via a storage collision

```solidity
contract Attack {
    address public a;          // slot 0 — aligns with proxy's `implementation`
    address public owner;      // slot 1 — aligns with proxy's `owner`
    function pwn() external { owner = tx.origin; }   // writes proxy's slot 1
}
// call proxy: proxy.delegatecall(attack.pwn()) → owner = attacker
```

The attack contract declares vars at the SAME slots as the proxy's protected
vars; its `delegatecall`ed function writes them.

### Hijack the implementation slot

If a settable var or the calldata controls the `delegatecall` target, point it
at a contract whose `delegatecall`ed code does `owner = msg.sender` (the
preserved original caller) or `selfdestruct`.

### The uninitialized library

A `WalletLibrary` with an `initWallet` `onlyOwner`-less init: `delegatecall`
into it and call `initWallet` → become the owner of the library's context in
the calling contract → `selfdestruct` (the parity wallet kill) or drain.

## The storage-collision table

A `delegatecall` writes by SLOT POSITION, not name. Mismatched layouts:

```
proxy:   slot0=impl_addr  slot1=owner   slot2=...
impl:    slot0=x          slot1=owner   slot2=balance
```

If impl writes `x` (its slot0) it overwrites the proxy's `impl_addr` — redirect
the next `delegatecall` to attacker code. The exploit reads both contracts'
declared layouts and finds the slot that becomes `owner`/`isSolved`.

## The evidence

`cast storage $PROXY 1` (the owner slot) = the attacker's address after the tx;
`isSolved() → true`. The receipt + the storage read are the proof.
