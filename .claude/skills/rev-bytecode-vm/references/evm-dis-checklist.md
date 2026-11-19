# EVM bytecode — the contract's check — checklist

Companion to `evm-dis.md`.

## Checklist

- [ ] PUSH1..32: push a constant — the expected bytes
- [ ] DUP/SWAP: stack ops
- [ ] EQ/LT/GT: compare
- [ ] ISZERO: negate
- [ ] JUMPI: conditional jump — the decision
- [ ] SHA3: a hash
- [ ] CALLDATALOAD: read input
