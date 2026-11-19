# Class boundaries — when this is the wrong skill

## rev-native-check instead

- A native ELF/PE, not bytecode → the deciding check is compiled
  x86/ARM, in rev-native-check.

## rev-managed-code instead

- A .NET managed assembly → ildasm/ilspy territory.
- Deep Java .class with framework layers → managed.

## misc-encoding-carrier instead

- An encoding puzzle — data encoded, no VM dispatch loop.

## The discriminator

This class needs a DISPATCH LOOP or a serialized CODE OBJECT — a
VM/bytecode that interprets. A direct native compare, a managed
runtime, or a pure encoding routes away.
