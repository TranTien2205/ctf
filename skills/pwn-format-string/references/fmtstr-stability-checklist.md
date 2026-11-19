# Offset stability — does N survive across calls? — checklist

Companion to `fmtstr-stability.md`.

## Checklist

- [ ] 1. Within one call site, N is constant.
- [ ] 2. Different call sites → different frames → possibly different N.
- [ ] 3. A recursive site → N shifts with depth.
