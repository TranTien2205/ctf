# Network recon: cidrscope

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Scope/CIDR reading: when scope grants a range
or subnet, enumeration widens per the grant - but each host
still gets the single-host recon flow. An ambiguous scope
(a /24 where one host was expected) = clarify, never assume;
the supplied target remains the anchor.
## Pivot

Signal harvested -> out-*; route named -> that skill.
