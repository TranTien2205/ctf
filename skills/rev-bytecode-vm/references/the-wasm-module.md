# .wasm — the module


WASM: sections (type/import/func/code/name), stack-machine
instructions — wasm_info.py inventories it:

    python3 tools/wasm_info.py mod.wasm --names

The name section's function names locate the check before
disassembly.
