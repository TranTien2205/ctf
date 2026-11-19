# Reentrancy — drain a contract through its own callback

## The shape

```solidity
function withdraw(uint _amount) public {
    require(balances[msg.sender] >= _amount);
    (bool ok, ) = msg.sender.call{value: _amount}("");   // external call FIRST
    require(ok);
    balances[msg.sender] -= _amount;                    // state update AFTER
}
```

The external `call` forwards gas and runs the callee's `receive`/`fallback`. The
callee is attacker code — it **calls back into `withdraw` before the balance is
decremented**, so the `require` passes again and the contract pays out
repeatedly. The bug is **checks-effects-interactions violated**: the effect
(`balances -=`) happens after the interaction (`.call`).

## The detection fingerprint

- an external `call`/`call{value:}` to `msg.sender` (or any caller-controlled
  address) BEFORE the state update
- the callee is the attacker (a contract they deployed with a `receive`/`fallback`)
- the protected state is a balance/flag the predicate reads
- **falsifier**: `.transfer`/`.send` (2300 gas — no room to re-enter), a
  `nonReentrant`/`locked` guard, or the state update already before the call

## The exploit contract

```solidity
contract Attack {
    Vulnerable v;
    constructor(address _v) payable { v = Vulnerable(_v); }
    function attack() external payable {
        v.deposit{value: msg.value}();
        v.withdraw(msg.value);
    }
    receive() external payable {
        if (address(v).balance >= 1 ether) v.withdraw(1 ether);
    }
}
```

`receive()` re-enters `withdraw` every time it gets paid — drains until the
balance can't cover another withdrawal or the predicate flips.

## The variants

| Variant | The shape |
|---|---|
| **single-function** | the same function re-entered — the classic drain |
| **cross-function** | re-enter a DIFFERENT function that shares the unsettled state (`withdraw` → `transfer` before the balance settles) |
| **cross-contract** | the callback re-enters a second contract sharing state |
| **read-only** | a `staticcall`'d view reads mid-transition state — an oracle that returns a stale balance to a third contract |
| **ERC-777/721 hooks** | `tokensReceived`/`onERC721Received` — a token transfer that calls the recipient, re-entering the sender |

## The forcing cases

- the function takes a `payable` deposit → seed it, then drain more than deposited
- the predicate is `balance == 0` → re-enter until drained
- the predicate is a flag on a count → re-enter to the count

## The trap

`gasleft()` inside `receive` — a `.transfer` leaves only 2300, enough for a log
but not a re-entering `call`. If `receive` can't call back, the guard is
`.transfer` or a `nonReentrant` — falsified. Check `cast gas` / the function
body for the call type before committing to the contract.
