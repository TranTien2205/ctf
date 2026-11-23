# API recon: idshape

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Identifier shape = enumeration prediction:
sequential int -> idor enumerable scope; UUIDv4 -> not
enumerable, leak-dependent; 24-hex -> MongoDB ObjectId
(timestamp+random) = nosqli prior; base64-encoded compound
(user:ts:sig) -> decode it; short hashids -> weak space.
Record the shape observed with its source response.
## Pivot

Signal harvested -> out-*; route named -> that skill.
