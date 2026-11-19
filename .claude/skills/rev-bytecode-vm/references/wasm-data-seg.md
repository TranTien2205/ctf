# The WASM data segment — where the constants hide

WASM memory is initialized by data segments — the expected flag
bytes often sit there rather than as i32.const immediates.

## The locate

    wasm-objdump -x mod.wasm    # section dump, if available
    # or parse the data section manually

## The read pattern

    i32.const 0x1000     ; address of expected[i]
    i32.load8_u          ; read expected byte
    local.get 0
    i32.xor
    ...

The expected bytes are read FROM MEMORY — the data segment holds
them, not the instruction stream.

## Extraction

Find the data segment bytes at the referenced offsets — those are
the expected constants to invert.
