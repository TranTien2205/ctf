# The IL instruction set — reading .NET

CIL is a stack machine: ldarg/ldloc load, stloc stores, ldc pushes
constants, ldstr pushes strings, call/callvirt invokes, br/brtrue/
brfalse branch, beq/bne compare-branches, ret returns.

## The check pattern

    ldarg input → transform (call/xor/add) → ldc/ldstr expected →
    beq/ceq + brfalse → verdict

The deciding instruction is the compare-branch after the transform.
