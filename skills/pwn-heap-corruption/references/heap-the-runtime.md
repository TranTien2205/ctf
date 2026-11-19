# The runtime view — what the process sees

Between the bug and the flag: the process's own behavior is the
verification channel when r2 -d isn't available.

## Observable ground truth

- The alloc's returned address (if the service prints it).
- The show() output's content — the leak channel.
- The abort's message — the check that fired.
- A crash vs a clean return — the binary signal.
- The next alloc's behavior — the bin state's echo.

## The discipline

Record each observed output against the predicted state — a divergence
is the diagnosis, not noise.
