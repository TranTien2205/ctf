# Knowing the write target's address


%n writes to *arg — arg must be the target's ADDRESS. Under non-PIE it's
a fixed constant; under PIE it's base+offset; on the stack it's a leaked
stack address.

## Steps

1. Choose the target (GOT slot, ret-addr, hook, global).
2. Get its address: static (non-PIE), base+offset (PIE), or leaked stack
   addr.
3. Pack it as the arg-position pointer.

## Commands

```bash
readelf -r ./chal
nm ./chal | grep -i ' [bdD] '
```

## Falsifier

The target's address is undeterminable: the write is blind.
