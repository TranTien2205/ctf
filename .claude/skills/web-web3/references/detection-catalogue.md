# Detection catalogue — every observable, indexed

## By the file it lives in

| File | The signals it lists |
|---|---|
| `detection.md` | the package signals — `.sol`, `Setup.sol`, RPC+key |
| `detection-deep.md` | the bytecode signals — the dispatch, SSTORE, the context ops |
| `detection-map.md` | the signal → class → file table |
| `detection-index.md` | the full signal table (predicate/source/bytecode/package) |
| `detection-matrix.md` | the predicate × primitive matrix |
| `detection-checklist.md` | the step-by-step detection check |
| `detection-surface.md` | the observable inventory |
| `detection-signals.md` | the signal-strength table |
| `detection-playbook.md` | the decision sequence |
| `detection-verdict.md` | the verdict levels |

## By the source

### Source-code signals

```
Setup.sol/isSolved()       → the predicate — the strongest signal
the contract's functions   → the reachable surface
the pragma                 → <0.8 wrap / >=0.8 revert
the keywords               → delegatecall/tx.origin/block.*/ecrecover/selfdestruct/...
the modifiers              → onlyOwner/nonReentrant/etc.
```

### Bytecode signals

```
the dispatch table         → the reachable functions (no source needed)
the SSTORE map             → which slots each function writes
the context ops            → ORIGIN/CALLER/TIMESTAMP/DELEGATECALL/...
the call-family ops        → CALL/DELEGATECALL/STATICCALL/SELFDESTRUCT
```

### State signals

```
the getters (cast call)    → the predicate-relevant values
cast storage               → the private + the predicate slots
cast balance               → the ether surface
cast logs / cast tx        → the emitted secrets / constructor args
```

### Package signals

```
Setup.sol + isSolved()     → the predicate-driven shape
RPC + private key          → the live instance
foundry/hardhat/truffle    → the toolchain
an ABI / a front-end       → the intended functions
```

## By the class it signals

`detection-index.md` + `detection-map.md` index every signal to its class —
the predicate-shape table aims the detection; the source/bytecode tables confirm
the primitive; the state table confirms the transition exists.
