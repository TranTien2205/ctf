# Input via argv — when the read is the command line — checklist

Some binaries take input as argv[1] instead of stdin: the overflow is in an argument. The payload goes in the argument position.

## Checklist

- [ ] Run ./chal <payload> locally — the arg IS the input.
- [ ] Send the cyclic as argv[1]; measure the offset from the fault.
- [ ] Remote: the arg goes in the command or a field of the protocol.
- [ ] Byte filters: argv can't contain \x00 (it terminates the arg).

## Abort conditions

- \x00 can't appear in argv — no null bytes in the payload.
- The shell interprets the arg — quote it or pass raw bytes via subprocess.

## Falsifier

Falsifier — the input isn't argv — check stdin/protocol paths.
