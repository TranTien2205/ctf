# Format-string as a leak primitive — feeding the smash — checklist

A format-string read isn't always the exploit — often it's the LEAK that feeds a stack-overflow chain: the canary, the PIE base, a libc pointer.

## Checklist

- [ ] Trigger the format read; dump the %p words.
- [ ] Extract the canary (00-ending word), the code pointer (PIE base), or the libc pointer.
- [ ] Feed the leaked values into the stack-overflow payload.
- [ ] The fmtstr is the leak; the smash is the exploit.

## Abort conditions

- The same fmtstr primitive that reads also writes — decide which you need.
- The leak is valid for the process instance — re-leak per exec.

## Falsifier

Falsifier — the leaked words don't contain the needed value, or the smash isn't exploitable anyway: the composition fails.
