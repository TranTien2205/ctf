# Cloud recon: azureblob

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Azure blob storage: <name>.blob.core.windows.net
/<container>?restype=container&comp=list = open listing XML;
StaticWebsiteConfig endpoint <name>.z*.web.core.windows.net;
container candidates (public/assets/backups) bounded list.
Status+XML error codes name existence verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
