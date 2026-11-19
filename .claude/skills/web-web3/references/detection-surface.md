# Detection surface — the full observable inventory

## The package surface

| Observable | The read |
|---|---|
| `Setup.sol` | the deploys + `isSolved()` — the predicate |
| `Challenge.sol` | the reachable functions + the bug signals |
| the RPC endpoint | the live private chain — `cast chain-id` |
| the private key | the attributable caller — `cast wallet address` |
| a `foundry.toml`/`hardhat.config`/`truffle` | the toolchain |
| an ABI / a front-end | the intended functions |

## The predicate surface

| `isSolved()` reads | The signal |
|---|---|
| a getter (`owner()`, `locked()`) | the var's setter is the target |
| a raw slot/`balance` | the state's writers are the target |
| `address(this).balance` | the ether routes — drain or force-feed |
| `extcodesize`/`code.length` | the code-presence — selfdestruct/constructor |
| a computed value (`answer`, `rate`) | the computation's source — randomness/accounting |

## The bytecode surface

| Observable | The signal |
|---|---|
| the dispatch table (`PUSH4 <sel>`) | the reachable functions |
| `SSTORE` ops | the state writes — which slots each function touches |
| `DELEGATECALL`/`CALL`/`STATICCALL` | the foreign-call primitives |
| `SELFDESTRUCT`/`CREATE`/`CREATE2` | the deploy/destroy primitives |
| `ORIGIN`/`CALLER`/`CALLVALUE` | the context reads |
| `TIMESTAMP`/`BLOCKHASH`/`NUMBER`/`DIFFICULTY`/`COINBASE` | the weak-randomness sources |
| `CODESIZE`/`EXTCODESIZE` | the EOA/contract check |
| `ECRECOVER`/`SHA3` | the signature/hash surface |
| `REVERT`/`INVALID` | the guards |

## The state surface

| Observable | The read |
|---|---|
| `cast call` the getters | the predicate-relevant values |
| `cast storage` the slots | the private + the predicate vars |
| `cast balance` | the ether the contract holds |
| `cast code` | the deployed bytecode (vs the `.sol`) |
| `cast logs`/`cast tx` | emitted secrets, constructor args |

## The caller surface

| Observable | The read |
|---|---|
| `cast wallet address --private-key $KEY` | the attributable EOA |
| `cast balance $ME` | the caller's ether — the deploy/send budget |
| `cast nonce $ME` | the next deploy address (CREATE) — `cast getAddress` |
