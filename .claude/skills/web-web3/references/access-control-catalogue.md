# Access-control catalogue — every unprotected-write case

## The bare setter — the default solve

```solidity
function setOwner(address o) public { owner = o; }        // no guard
function unlock() public { locked = false; }               // no guard
function setFlag(bool f) external { solved = f; }
function changeOwner(address o) public { owner = o; }
function transferOwnership(address o) public { owner = o; }
```

`cast send` it — the cheapest solve. Check it FIRST.

## The re-initialization

```solidity
function initialize(address o) public {           // callable post-deploy
    require(!initialized);
    owner = o; initialized = true;
}
// if `initialized` isn't set, or in the wrong context → callable
```

`uninitialized-proxy.md` — the init owns the context it's called in.

## The default-visibility (pre-0.5)

```solidity
function owned() { owner = msg.sender; }   // no keyword → public (pre-0.5)
```

A visibility-less `function` in `pragma <0.5` is `public` — an `internal`-
intended function is callable.

## The constructor-as-function (pre-0.5)

```solidity
contract X {
    function X() { owner = msg.sender; }   // the constructor (pre-0.5 name-style)
    function x() { owner = msg.sender; }   // a TYPO — a callable function!
}
```

A mis-cased `function x()` is a regular public function that sets `owner`.

## The forgotten-internal

```solidity
function _init() public { owner = msg.sender; }   // _-named but public
function internalHelper() public { ... writes owner ... }
```

An `_`-prefixed or `internal`-intended function left `public`.

## The fallback-writes-owner

```solidity
fallback() external { if (msg.data.length == 0) owner = msg.sender; }
```

A `fallback`/`receive` that writes the owner/flag — send a raw call.

## The guard-bypass shapes

| The guard | The bypass |
|---|---|
| `onlyOwner` + `setOwner`/`init`/`transferOwnership` open | own it first |
| `require(msg.sender == tx.origin)` | a constructor call (extcodesize 0) |
| `require(tx.origin != msg.sender)` | a contract in the middle |
| `require(!locked)`, `locked` settable | the unlock |
| `require(sig valid)` | a replayed/forged sig |
| `require(x == privateVar)` | `cast storage` the var |

## The role-granularity case

`onlyRole(MINTER)`/`onlyRole(ADMIN)` — a role that's grantable (`grantRole`
open), a role with too much power, or a `hasRole` check that reads the wrong
slot. The role's grant function is the surface.

## The evidence

`cast call` the owner/locked getter before/after; `isSolved() → true`.
