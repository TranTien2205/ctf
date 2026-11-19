# The function list — afl's inventory


    r2 -A ./chal ; afl

Every function: sym.imp.* (imports), sym.* (library/runtime), loc.*
and fcn.* (the binary's own code).

## The useful rows

- main / the vuln function — the re-entry target.
- win/flag/system-looking names — the shortcut ending.
- sym.imp.* — the PLT-callable imports.
