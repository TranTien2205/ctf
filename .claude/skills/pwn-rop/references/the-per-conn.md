# The per-connection — fresh each connect


A per-connection process: each connect is a fresh process — the leak
in connect 1 helps connect 2 ONLY if ASLR/addresses persist
(fork-server) — usually they don't; the single-connection chain is
the shape.
