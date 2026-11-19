# 12 vs 16 byte headers — deep

Companion to `pyc-header-offset.md`.

3.7+ uses a 16-byte header (magic+flags+hash); older uses 12. marshal.loads(d[16:]) or d[12:] — the wrong offset fails before the code object parses.
