# The two overflows — delivering two stages


When the exploit needs two stages, they're two separate overwrites
of the same vuln — the program re-enters between them.

## The sync

Between stage 1 (leak) and stage 2 (fire), the script computes —
the recv of the leak unblocks the stage-2 assembly.
