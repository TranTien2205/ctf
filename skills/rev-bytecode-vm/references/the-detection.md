# Detection — when this class applies


The signature: logic lives in bytecode — a .pyc/.class/.wasm/serialized
code object, or a custom dispatch-loop VM.

## Boundary

- Native x86/ARM binary → rev-native-check.
- .NET/Java managed → rev-managed-code.
- Just an encoding (no VM) → misc-encoding-carrier.
