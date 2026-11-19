# The patch — flipping the verdict


When replication is impossible: patch the deciding jump — jz↔jnz, or
nop the branch — the binary then accepts anything.

## The r2 way

    r2 -w ./chal
    wa jne <addr> @ <the_jz_addr>    # or wa nop

## The limit

A patched binary proves reachability, not the input — the flag may
need the real input (the check protects the flag's USE, not just a
verdict print).
