# The send path — getting bytes down the wire — checklist

Companion to `the-send-path2.md`.

## Checklist

- [ ] The script packs correctly (the self-check).
- [ ] The socket sends all (sendall, not send).
- [ ] The service's read accepts them (the length and the terminators).
- [ ] The frame's layout matches the measured offset.
