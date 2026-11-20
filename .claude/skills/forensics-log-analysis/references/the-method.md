# The method field — odd verbs

GET/POST dominate; a PUT/DELETE/OPTIONS/PROPFIND or a custom verb
is the anomaly — the method distribution catches it.

## The find

    awk '{print $6}' access.log | sort|uniq -c|sort -rn

A single PUT (a dropped file), a PROPFIND (WebDAV enumeration), a
CONNECT (proxy misuse) — the odd verb names the technique.
