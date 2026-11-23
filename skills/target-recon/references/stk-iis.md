# Stack playbook: iis

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

IIS: Server: Microsoft-IIS/x.y, .asp/.aspx/.ashx/.asmx
extensions, ASP.NET_SessionId, X-Powered-By: ASP.NET.

Recon checks:
- IIS version maps to Windows version exactly
- /trace.axd -> request trace surface (classic leak)
- .ashx handlers -> generic-handler surface
- WebDAV verbs (OPTIONS reveals PUT/DELETE allowed)
- Tilde enum (~1) for 8.3 shortname = file-name oracle
- /iisstart.htm + /inetpub defaults

Predicts: shortname enumeration, webdav write surfaces,
deserialization via ViewState, file-read.
## Pivot

Signal harvested -> out-*; route named -> that skill.
