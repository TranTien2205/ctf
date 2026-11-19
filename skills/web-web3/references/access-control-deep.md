# Access control (deep) — every unprotected-write shape

## The reachability enumeration

The whole class reduces to: **which reachable function writes a slot
`isSolved()` reads, and is it callable by the supplied caller?**

Enumerate the external/public non-view functions from the source or the
dispatch table. For each, trace its `SSTORE`s — the unguarded one writing the
predicate's slot is the bug.

## The guard taxonomy

| Guard | The bypass |
|---|---|
| NONE — a bare `setOwner`/`unlock`/`setFlag` | call it directly — the intended solve more often than not |
| `onlyOwner` where `owner` is uninitialized/zero | a `address(0)` owner, or an `init` that sets it |
| `onlyOwner` where `owner` is settable | a `setOwner`/`transferOwnership` that's itself unguarded |
| `require(msg.sender == tx.origin)` | a constructor call (extcodesize 0) — see `tx-origin-deep` |
| `require(msg.sender == signer)` where signer is `ecrecover`-derived | a forged/replayed sig — see `signature-replay` |
| `require(!locked)` where `locked` is settable | the unlock setter |
| `require(block.number > N)` | wait / the predicate's time check |
| a modifier that checks a DIFFERENT var | the guard protects the wrong slot |

## The unprotected-setter shapes

### Bare setter

```solidity
function setOwner(address o) public { owner = o; }    // no guard → anyone owns
```

### Re-initialization

```solidity
function initialize(address o) public {               // callable post-deploy
    owner = o;   // or a reset flag the init re-runs on
}
```

### Default visibility (pre-0.5)

```solidity
function owned() { owner = msg.sender; }   // no keyword → defaults public
```

Pre-0.5 Solidity defaults a visibility-less `function` to `public` — an
`internal`-intended function is callable.

### Constructor-as-function (pre-0.5 name-constructor)

```solidity
contract X { function X() { owner = msg.sender; } }
// or a typo: function x() — cased differently, becomes a NORMAL function
```

The old name-constructor pattern: a function with the contract's name was the
constructor — but a MIScased `function x()` (lowercase) is a regular callable
function that sets `owner`.

## The "the setter is gated, the gate is the bug" case

The setter has `onlyOwner` — but `owner` itself is settable elsewhere, or the
guard compares a `private`-but-readable var, or the `init` that sets `owner` is
callable. The access-control bypass is the GATE's weakness, not the setter's
absence.

## The evidence

`cast call $CH "owner()(address)"` / the predicate getter → the caller or the
flipped value; `isSolved() → true`. One `cast send` is the whole exploit when
the setter is bare.
