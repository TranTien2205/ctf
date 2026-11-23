# Tool output parsing: nmapout

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

nmap output -> observations: PORT STATE SERVICE
VERSION lines verbatim; -sV version strings = stack
identity; script output (http-title, http-methods) = surface
facts. One port only, recorded - the script results are
observations like any response.
## Pivot

Signal harvested -> out-*; route named -> that skill.
