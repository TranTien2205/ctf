# Param discovery: contenttype

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Content-Type swap: resend one request as
form-urlencoded, then JSON, then multipart, then XML - each
accepted type is a different parser = different bug classes
(json->nosqli/proto, xml->xxe, form->classic). 415 responses
name the allowed set; record the accept matrix, not a verdict.
## Pivot

Signal harvested -> out-*; route named -> that skill.
