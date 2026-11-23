# Output: classify the signals

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

python3 tools/classify.py "<observation list>"
- the signal list becomes the classifier's
input; recon ends where classification begins.

## Pivot

Signal harvested -> out-*; route named -> that skill.
