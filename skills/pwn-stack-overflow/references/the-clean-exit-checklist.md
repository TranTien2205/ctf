# The clean-exit path — landing the flag without a crash — checklist

Companion to `the-clean-exit.md`.

## Checklist

- [ ] After the chain runs, the process may continue or exit — a clean exit
- [ ] through atexit, destructors, or a return-path matters when you need the
- [ ] service to keep running or print the result.
- [ ] A ret2system whose 'return' jumps to a clean-exit function keeps the
- [ ] service alive for the response.
- [ ] An atexit-registered cleanup runs on exit — a controlled atexit is a
- [ ] call-site.
- [ ] A chained 'exit@plt' or the like closes the process predictably.
- [ ] A chain that lands the exec but crashes the process before the flag
- [ ] prints. The clean-exit keeps the output readable.
