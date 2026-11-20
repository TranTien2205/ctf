# Worked — a PNG LSB

1. file/png-check → real PNG, no appended data.
2. lsb_scan --planes 1 → a printable stream on b1,rgb,lsb.
3. The stream decodes to flag{...} — verify, hook.
