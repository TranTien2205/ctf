# The redirect effect — what the write actually triggers — checklist

Companion to `the-redirect-effect.md`.

## Checklist

- [ ] GOT[x] written → the next call to x goes to your target.
- [ ] ret-addr written → the function's return goes to your target.
- [ ] __free_hook written → the next free calls your target.
- [ ] A vtable/handler written → the next indirect call redirects.
