# The function table — what the binary has


afl lists every function — the win functions, the helper code, the
main loop:

- win/flag/shell functions — the short ending.
- main/the vuln function — the re-entry target.
- imported PLT stubs — the call surface.

## The check

    r2 -A ./chal ; afl | grep -iE 'win|flag|main|vuln'
