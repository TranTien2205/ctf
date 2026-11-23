# Service recon: ssh

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SSH banner: 'SSH-2.0-<server>_<version>' verbatim in the
first line (OpenSSH_8.9p1, dropbear, libssh). The software+version
is the whole recon product - it names the exploit matrix if a
known vuln applies, and the auth methods list comes from one
failed auth attempt (publickey,password). No brute-force in
recon.
## Pivot

Signal harvested -> out-*; route named -> that skill.
