# Path enum: uploaddirs

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Upload-directory probes: /uploads /upload
/files /media /static/uploads /images /attachments /user/files
- open listing (Index of) = inventory, 403 = exists-gated,
200-empty = exists-empty. Combine with the upload form's
stored-path naming to predict retrieval.
## Pivot

Signal harvested -> out-*; route named -> that skill.
