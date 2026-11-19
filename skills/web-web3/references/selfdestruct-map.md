# selfdestruct map — the destruction and force-feed shapes indexed

## The shape → the predicate it satisfies

| The shape | The predicate |
|---|---|
| **force-feed** — `selfdestruct` into a no-receive contract | `address(this).balance > 0` — ether despite refusing it |
| **code-delete** — `selfdestruct` erases the code | `extcodesize(addr) == 0` / "the contract is gone" |
| **library-kill** — `selfdestruct` in a delegatecall'd lib | destroys the CALLER — the wallet-kill |
| **the drain-break** — `selfdestruct` a contract the predicate reads | the predicate reads its code/balance |

## The force-feed family

```solidity
// fund + force-feed
contract Force {
    constructor() payable {}
    function boom(address t) external { selfdestruct(payable(t)); }
}
// the selfdestruct sends ALL of Force's balance to t — no code run on t
```

The only way to give ether to a contract that rejects `call{value}`/`.transfer`.

## The code-deletion family

`selfdestruct` erases the caller's code+storage — a predicate `code.length == 0`
or `extcodesize == 0` is solved by it. The CALLER is destroyed — a
`delegatecall`ed `selfdestruct` destroys the CALLING contract.

## The Cancun rule

Post-EIP-6780, `selfdestruct` only fully deletes code+storage for a
same-transaction-created contract — otherwise it sends the ether but the code
persists. The force-send works either way; the code-deletion needs the
same-tx rule or a pre-Cancun chain. Check which the challenge is on.

## The CREATE2-resurrect

A selfdestructed contract's address is re-deployable via CREATE2 (same deployer,
salt, initcode) — code returns to a "deleted" address. A predicate that cached
`extcodesize == 0` is bypassed by the resurrect.

## The detection order

```bash
# the predicate is a balance/code check?
cast call $CH "isSolved()(bool)" --rpc-url $RPC
# is there a selfdestruct in the code?
cast code $CH --rpc-url $RPC | evm disasm | grep -i selfdestruct
# can a contract be funded + selfdestructed into the target?
```

## The falsifier map

| The falsifier | Closes |
|---|---|
| the predicate isn't a balance/code check | the force-feed/delete is irrelevant |
| no `selfdestruct` reachable AND the contract accepts ether | the force-feed isn't needed |
| the `selfdestruct` isn't in a callable path | the delete isn't reachable |

`selfdestruct.md`/`selfdestruct-deep.md` for the full shapes.
