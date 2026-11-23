# Response reading: bodystruct

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Body-structure reading: JSON vs HTML vs text
vs binary; JSON error vs HTML error on the same endpoint =
two render paths; embedded templates in JS strings;
base64 chunks in bodies (data leaks or blobs). The content-
type+shape pair per response is the observation.
## Pivot

Signal harvested -> out-*; route named -> that skill.
