# IoT/embedded recon: firmwareendpoints

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Firmware-surface endpoints: /rom-0,
/setup.cgi, /apply.cgi, /goform/, /HNAP1, /boaform/,
/currentsetting.htm - each names a vendor's management
protocol (HNAP = D-Link, goform = Tenda). One probe each;
the 200/403 split maps which handlers exist.
## Pivot

Signal harvested -> out-*; route named -> that skill.
