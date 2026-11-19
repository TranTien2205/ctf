# The dead write — aiming at memory nobody reads — checklist

Companion to `the-dead-write.md`.

## Checklist

- [ ] GOT/ret: fires on call/return — will the program reach it?
- [ ] Hook: fires on malloc/free — does one happen after?
- [ ] FILE: fires on stdio/exit — is exit reachable?
- [ ] App ptr: fires on its call — is the call reachable?
