# IoT/embedded recon: defaultcreds

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Default-credential inventory: admin/admin,
admin/password, root/root, admin/<blank>, user/user,
support/support, the ISP pairs (admin/alpine#fbr etc). ONE
login attempt per likely pair is recon; a list per device
family sits in vendor defaults - record which pair the
banner/title suggests, not a sprayed set.
## Pivot

Signal harvested -> out-*; route named -> that skill.
