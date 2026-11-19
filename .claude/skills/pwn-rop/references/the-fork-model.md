# The fork model — the server that forks


A fork-server: the parent accepts, the child handles — the child's
memory (incl. canary, base) is the parent's copy — leaks persist
across children (the brute-forceable canary's basis).
