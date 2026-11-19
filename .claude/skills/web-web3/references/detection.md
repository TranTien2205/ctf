# Detection — naming the class from the challenge package

## The package signals

The class announces itself in the challenge files — no web fingerprint needed:

| Signal | The class |
|---|---|
| a `*.sol` source file | solidity challenge |
| `Setup.sol` + `isSolved()` | the setup-predicate shape |
| an RPC URL + a private key | a live private chain |
| `cast`/`forge`/`web3`/`ethers` in the handout | the interaction toolchain |
| `foundry.toml`/`hardhat.config`/`truffle` | the dev framework |

## The setup-predicate read

The first read is `Setup.sol`:

```solidity
contract Setup {
    Challenge public challenge;
    constructor() { challenge = new Challenge(); }
    function isSolved() public view returns (bool) {
        return /* the predicate */;
    }
}
```

The predicate names the target state. Record:
- the **challenge address** — `setup.challenge()` or the deploy log
- the **solved predicate** — the exact boolean expression
- the **starting state** — read it with view calls before transacting

## The source-vs-bytecode check

The shipped `.sol` may not be the deployed code. Disassemble the live bytecode:

```bash
cast code $CHALLENGE --rpc-url $RPC      # the deployed bytecode
```

A challenge whose source hides the real logic ships bytecode that differs —
the `evm disasm`/`heimdall`/`panoramix` decompile is then the real source of truth.

## The read-only probe pass

Before any transaction, read everything the predicate and the contract expose:

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
cast call $CHALLENGE "owner()(address)" --rpc-url $RPC
cast call $CHALLENGE "locked()(bool)" --rpc-url $RPC
cast balance $CHALLENGE --rpc-url $RPC
cast storage $CHALLENGE 0 --rpc-url $RPC   # slot 0
cast storage $CHALLENGE 1 --rpc-url $RPC   # slot 1
```

`cast storage` reads any slot — a `private` var is not secret. The starting
state names which class of transition is needed.

## The reachable-call inventory

List the external/public functions and which change state:

```
non-view, non-pure public/external functions = the reachable transitions
a function callable by msg.sender with no onlyOwner/onlyX guard = the open setter
```

The candidate exploit is the reachable call whose post-state satisfies the
predicate. The class-signal table (which function shape → which bug) is in
`attack-shapes.md` / per-bug-*.md.
