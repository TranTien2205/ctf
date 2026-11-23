# Class recheck: nosqli

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-nosqli needs: JSON body acceptance
(object-typed values reach the parser), ObjectId-shaped ids
(24-hex = mongo prior), login/compare endpoints that answer
differently per input shape, and qs-array syntax (?a[]=)
working. Deliver: which endpoint accepts object params and
the verbatim response for a plain-string vs object probe.
## Pivot

Signal harvested -> out-*; route named -> that skill.
