# Wordlist selection: bystack

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Wordlist by stack: PHP targets get .php/.txt/.bak
extensions; IIS gets .asp/.aspx; Java .jsp/.do/.action;
generic gets no-extension + .txt + .old. raft + the stack's
extension list beats generic lists - wrong-extension hits are
wasted requests.
## Pivot

Signal harvested -> out-*; route named -> that skill.
