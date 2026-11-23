# IoT/embedded recon: embweb

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Embedded web UI recon: goahead/uhttpd/mini_httpd
server headers, /cgi-bin/ handlers, login.asp/.htm pages,
device model in title/footer ('D-Link', 'OpenWrt LuCI',
'RouterOS'). Default-cred pairs are the documented recon
check on embedded targets; the cgi handlers are the
command-injection priors.
## Pivot

Signal harvested -> out-*; route named -> that skill.
