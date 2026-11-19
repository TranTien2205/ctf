# Per-class map — the class → the contract type → the mechanism

## The class-by-contract-type table

| Contract type | The likely classes |
|---|---|
| a `Setup`/`Challenge` pair | the predicate-driven solve — whichever mechanism the predicate's state needs |
| a `Proxy`/`Implementation` | delegatecall, storage-collision, uninitialized-proxy |
| a `Vault`/`Bank`/`Wallet`/`Token` | reentrancy, accounting, overflow, the force-feed |
| a `Library`/`WalletLibrary` | delegatecall-into-code, the uninitialized init + kill |
| a `Lottery`/`Guess`/`Flip`/`Random` | weak-randomness |
| a `Lock`/`Locked`/`Vault-locked` | visibility (a private secret gate) |
| a `Shop`/`Buyer`/`Elevator`/`Gate` | the interface-mismatch, the tx.origin/gasleft check |
| a `King`/`Denial`/`DOS` | the refusing-partner, the loop-DOS |
| a `Preservation`/`PuzzleWallet` | delegatecall/storage-collision |
| a `Recovery`/`SimpleToken`/`Creator` | the lost-address/CREATE |
| a `Dex`/`Staking`/`Farm`/`FlashLoan` | accounting-vault, flashloan-oracle |
| a `Gatekeeper`/`Switch`/`Privacy` | the data-derived key, the EOA check, the private-unlock |
| an `AlienCodex`/`array` | the array-length underflow (pre-0.8) |
| a `Motorbike`/`Engine` | the uninitialized-implementation + selfdestruct |
| a `HigherOrder`/`ABI`-smuggle | the calldata-encoding bug |
| a `DoubleEntryPoint`/`CryptoVault` | the token-sweep, the fortified-function guard |

## The class-by-predicate table

| Predicate | The classes |
|---|---|
| `owner() == X` | access-control, tx.origin, delegatecall, storage-collision |
| `balance == 0`/`> K` | reentrancy, selfdestruct, accounting |
| `flag`/`locked`/`solved` | access-control, visibility |
| `count`/`balances` | integer-overflow, reentrancy, accounting |
| `answer`/`winner` | weak-randomness, front-running, visibility |
| `code.length`/`extcodesize` | selfdestruct, constructor-EOA |
| `signer`/`verified` | signature |
| `rate`/`shares`/`price` | accounting-vault, flashloan-oracle |

## The per-class "the one thing to check first"

| Class | Check first |
|---|---|
| access-control | the bare setter — `cast send` it |
| reentrancy | the call-type — `.transfer` falsifies it |
| delegatecall | the impl's `SSTORE` map — which proxy slots it writes |
| integer-overflow | the pragma + `unchecked`/`SafeMath` |
| weak-randomness | the `block.*`/`private` source — same-block predict |
| tx.origin | the check — `!=`/`==`/`=` |
| selfdestruct | the predicate is a balance/code check |
| storage-collision | the proxy/impl slot layouts — diff them |
| signature | the hash's fields — nonce/chainid/sender |
| accounting | the donation/reentrancy path desyncs the tracked value |
