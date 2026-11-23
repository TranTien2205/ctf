# Service x next: redis / classify

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

After `redis` recon, whether the route is `classify`.

## Read

enough protocol signals -> straight to classify.py.
