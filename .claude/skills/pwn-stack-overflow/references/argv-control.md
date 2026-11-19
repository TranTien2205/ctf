# Input via argv — when the read is the command line

Some binaries take input as argv[1] instead of stdin: the overflow is in an argument. The payload goes in the argument position.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| main uses argv[1] directly | argv input | the arg is the buffer |
| copied into a stack buffer | argv overflow | argv[1] = payload |

## Steps

1. Run ./chal <payload> locally — the arg IS the input.
2. Send the cyclic as argv[1]; measure the offset from the fault.
3. Remote: the arg goes in the command or a field of the protocol.
4. Byte filters: argv can't contain \x00 (it terminates the arg).

## Falsifier

Falsifier — the input isn't argv — check stdin/protocol paths.

## Traps

- \x00 can't appear in argv — no null bytes in the payload.
- The shell interprets the arg — quote it or pass raw bytes via subprocess.

## Commands

```bash
./chal $(python3 -c 'print("A"*100)')
```

## Cross-references

`read-family.md`
