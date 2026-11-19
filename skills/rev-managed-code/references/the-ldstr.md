# ldstr — the IL string load

The IL instruction `ldstr` pushes a #US-heap literal — the compare
feeds on it. A check like `input == "expected"` compiles to:

    ldarg.0            ; input
    ldstr "expected"   ; the literal
    call string::Equals
    brfalse fail       ; the deciding branch

The ldstr's operand IS the expected value — read it from #US.
