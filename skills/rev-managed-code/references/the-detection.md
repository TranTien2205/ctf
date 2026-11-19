# Detection — when this class applies

The signature: a managed artifact — a PE with a CLR dir, a .class/
.jar, a .dex/.apk — whose check decompiles.

## Boundary

- Native only → rev-native-check.
- Pure bytecode (.pyc, custom VM) → rev-bytecode-vm.
- A .NET that's really AOT → native.
