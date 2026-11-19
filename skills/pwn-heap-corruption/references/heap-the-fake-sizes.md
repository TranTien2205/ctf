# Common fake sizes — the 0x41 and friends


The frequently-forged size values:

- 0x41: a small fastbin-ish chunk — the classic fake.
- 0x71: the 0x7f-preceded fastbin fake (the __malloc_hook trick).
- 0x101: a smallbin-sized fake.
- 0x21: the minimum useful chunk.

Each carries P set — the "next" chunk's size must still parse.
