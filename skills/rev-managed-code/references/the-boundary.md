# Class boundaries — the routing

- A PE with NO CLR dir, or AOT-compiled → rev-native-check.
- A .pyc / a pure bytecode program → rev-bytecode-vm.
- Managed code that's really a launcher → trace what it loads.
