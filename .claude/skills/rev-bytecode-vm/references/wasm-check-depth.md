# The .wasm check — reading the verification function

A WASM module's check is a function in the code section. Locate it
by name, read its instruction sequence.

## wasm_info first

    python3 tools/wasm_info.py mod.wasm --names

The name section's function names — check_flag, verify, validate —
locate the deciding function without disassembling everything.

## The instruction set

WASM is a typed stack machine:

- local.get/global.get: load a value
- i32.const: push a constant
- i32.xor/i32.add/i32.eq/i32.eqz: the ops
- call: a helper
- br_if/if: the branch
- i32.load8_u: read a byte from memory

## The check pattern

    local.get 0        ; input[i]
    i32.const 0x37
    i32.xor
    i32.const 0x52
    i32.eq
    i32.eqz
    br_if fail

The expected bytes and the transform are in the instruction stream.

## The data segment

The expected constants may sit in a data segment (memory init) —
dump it:

    wasm_info or wasm-objdump -x
