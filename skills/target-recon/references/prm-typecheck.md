# Param-level recon: typecheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Per-param type check: what does the endpoint accept -
int, string, object, array, bool? Type confusion probes
(int->string->object) reveal parser leniency = nosqli/logic
priors. Record accepted types per param verbatim; a param
that silently coerces is a different surface than one that
400s.
## Pivot

Signal harvested -> out-*; route named -> that skill.
