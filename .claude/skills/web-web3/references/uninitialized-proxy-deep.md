# Uninitialized proxy (deep) — the init-context split

## The two storages

A proxy pattern has TWO contracts with separate storage:

```
Proxy          — holds the STATE (its own slots); delegates calls to impl
Implementation — holds the CODE; its own storage is usually empty/unused
```

`initialize` sets `owner`/`initialized` — but which storage? `delegatecall` runs
impl code on PROXY storage, so `initialize` called THROUGH the proxy writes the
proxy's `owner`. Called DIRECTLY on the impl, it writes the IMPL's own storage.

## The three bugs

### 1. The impl's init is callable

The impl contract is deployed and uninitialized — call `initialize` on the impl
directly → own the impl's storage. Usually harmless (the impl's storage is
unused), BUT if the impl can `selfdestruct` or the predicate reads the impl's
state, that's the bug.

### 2. The proxy's init is callable

The proxy was deployed but `initialize` never ran on it (or can re-run) — call
it through the proxy → own the proxy's `owner` slot. The `initialized` flag in
the impl's storage doesn't protect the proxy's separate flag slot.

### 3. The `initialized` flag in the wrong context

`initialize` sets `initialized = true` in IMPL storage (a direct call), but the
proxy's `initialized` slot stays `false` → calling `initialize` through the
proxy passes the check → re-init the proxy's storage.

## The detection

```bash
cast call $IMPL "initialized()(bool)" --rpc-url $RPC    # the impl's flag
cast call $PROXY "initialized()(bool)" --rpc-url $RPC   # the proxy's flag (through the proxy)
cast storage $PROXY <owner-slot> --rpc-url $RPC          # the proxy's owner
cast storage $IMPL <owner-slot> --rpc-url $RPC           # the impl's owner
```

The flag check in BOTH contexts — a `false` in the proxy's context means the
proxy's `initialize` is callable.

## The parity-wallet shape

`WalletLibrary` (the impl) had `initWallet` — calling it DIRECTLY on the library
owned the library's context, then `kill` selfdestructed the LIBRARY. The
wallet contracts that `delegatecall`ed into it kept working storage-wise, but
the shared code was gone — the freeze.

The CTF variant: the impl's `init` is callable → own it → a `selfdestruct` in
the impl kills the impl's code → the proxy now delegates to an empty address.

## The evidence

`cast call`/`cast storage` the `owner`/`initialized` after the init — the
caller owns the context that was uninitialized. The init tx + the owner read
are the chain.
