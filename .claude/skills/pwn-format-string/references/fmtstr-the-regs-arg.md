# Register args as leak sources — rsi..r9 values


%1$p-%6$p (x64) read the register args — the caller's outgoing arguments
to printf: often rsi=a pointer, rdx=a size — real values leaking call
state.

## Steps

1. The register args hold whatever the caller passed — often useful
   pointers.
2. rsi may be a buffer pointer; rdx a length.
3. These are the call's actual varargs — not stack memory.

## Falsifier

The register args hold nothing useful (small ints): only the stack args
leak.
