# The bytecode-VM workflow


1. Identify: magic/header → format + version.
2. Inventory: pyc_dis --strings / wasm_info --names.
3. Locate: the check function/program.
4. Decode: dis / opcode table.
5. Extract: the expected + the transform.
6. Produce: the accepted input.
7. Verify: run the real program.
