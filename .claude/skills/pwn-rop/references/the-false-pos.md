# False positives — the non-signals


- A gadget listed but with a fatal mid-tail — not usable.
- A leak value that's a small int — the wrong field.
- A "shell" that echoes your input — a fake (or a cat).
- A clean exit — not a flag.
- A crash at a controlled address — control, not exploitation.
