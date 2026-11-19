# BIND_NOW — the eager resolve


Full RELRO's BIND_NOW: every import resolves at load — the GOT is
already final (read it for leaks) but read-only (no writes).
