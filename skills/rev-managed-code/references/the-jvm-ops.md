# The JVM ops — reading Java bytecode

The JVM is a stack machine: aload/iload load, ldc pushes a constant,
invoke* calls, if_icmp*/if_acmp*/ifeq/ifne compare-branches,
iadd/ixor arithmetic, tableswitch/lookupswitch the switch.

## The deciding ops

ifeq/ifne/if_icmpeq/if_acmpeq after the transform — the branch to
win or fail.
