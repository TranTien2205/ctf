# Delivering the chain — socat and stdlib — checklist

Companion to `the-delivery.md`.

## Checklist

- [ ] \x0a inside the payload ends a line-based read.
- [ ] \x00 in an address truncates a gets-style read.
