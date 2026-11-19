# Worked — the .wasm check


1. wasm_info --names: check_flag function named.
2. Its body: i32.eqz + br_if on each char.
3. The expected bytes in a data segment.
4. Replicate → accepted.
