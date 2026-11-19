# __stack_chk_guard — the canary's source


The master canary value sits in __stack_chk_guard (or TLS) — a read
of it is the canary leak; it's per-process constant.
