# The common size classes in CTF services


Menu services cluster around a few sizes — the ones the struct fields
suggest:

- 0x30-0x40: small objects (id + one ptr + small buf).
- 0x90-0x100: medium (name + desc).
- 0x200+: large (big content fields).

Match the exploit's sizes to what the service offers — a technique
needing a 0x500 chunk dies if max alloc is 0x100.
