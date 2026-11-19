# EVM bytecode — the contract's check

An EVM contract's bytecode: PUSH/DUP/SWAP/ISZERO/JUMPI ops — the
deciding branch is a JUMPI guarded by ISZERO or EQ.

## The ops

- PUSH1..32: push a constant — the expected bytes
- DUP/SWAP: stack ops
- EQ/LT/GT: compare
- ISZERO: negate
- JUMPI: conditional jump — the decision
- SHA3: a hash
- CALLDATALOAD: read input

## The check

    CALLDATALOAD 0     ; read input
    PUSH1 0x37
    XOR
    PUSH1 0x52
    EQ
    ISZERO
    PUSH2 fail
    JUMPI             ; jump if not equal

## Tools

evm disasm or the readable ops — the PUSH constants hold the
expected values.
