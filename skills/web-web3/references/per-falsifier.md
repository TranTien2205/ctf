# Per-falsifier map — the falsifier → the class it closes

| Falsifier | Closes |
|---|---|
| `.transfer`/`.send` (2300 gas) | reentrancy via `call` — no room to re-enter |
| a real `nonReentrant` guard on every function sharing the state | reentrancy |
| checks-effects-interactions (state before the call) | reentrancy |
| `>=0.8` pragma, no `unchecked`, SafeMath | integer-overflow |
| `initialized` true in the relevant context | uninitialized-proxy |
| the impl slot hardcoded, layouts verified | delegatecall/storage-collision |
| `msg.sender`-based auth (no `tx.origin`) | tx.origin |
| no `delegatecall`/`call`-to-caller in the code | reentrancy / delegatecall |
| a commit-reveal / VRF | weak-randomness / front-running |
| `blockhash`/`timestamp` not in the decision | weak-randomness |
| the sig binds nonce+chainid+sender+expiry, `s` low | signature |
| a pull-payment pattern (no push `transfer`) | gas-griefing (the refusing partner) |
| the predicate reads a slot NO function writes | the whole class |
| every reachable function guarded | access-control |
| the contract accepts ether normally | selfdestruct force-feed unnecessary |

## The class-closing falsifier

The predicate reads a set of slots; enumerate every reachable `SSTORE` to those
slots. If NONE is reachable by the supplied caller (or their contracts), the
class is closed — no transition reaches the solved state. Record the full
enumeration in the negative-result.

## The per-path falsifier record

Each bug-class's file lists its falsifier. When observed, record:

```text
the path          — the bug class
the falsifier     — the observation that closed it
the evidence      — the cast output showing it
```

`hooks.py post-probe --verdict falsifies` + `decide.py` routes to the next class.
