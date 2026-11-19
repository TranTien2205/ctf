# VM obfuscation — the layered interpreter

## Nested VMs

A VM whose program IS another VM's bytecode — recover each layer's
table separately.

## Dynamic opcodes

Opcodes remapped at runtime — the table is a function of state;
trace it.

## The angle

Obfuscation delays the table recovery — the falsifier (runtime
generation) routes to tracing.
