# PLT vs GOT — the two redirections


- Writing the GOT entry: the next PLT call jumps to your address —
  the redirect.
- You can't write the PLT (it's code, read-only) — the GOT is the
  writable side of the pair.
