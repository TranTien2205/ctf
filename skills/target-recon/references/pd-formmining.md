# Param discovery: formmining

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Form mining: every <form> in harvested HTML -
action (endpoint), method (verb), input names + types + values
(hidden fields are pre-filled parameters the author chose),
enctype (multipart = upload surface). A form's fields are the
author's own param list - no guessing needed.
## Pivot

Signal harvested -> out-*; route named -> that skill.
