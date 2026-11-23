# Service recon: ftp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

FTP banner grab: 220 <banner> names server+version
(vsFTPd 2.3.4 = the classic). Anonymous login attempt (USER
anonymous) = the only write-shaped recon allowed - it is the
documented recon question. 530 vs 230 verbatim. PASV port
behavior noted for later file access.
## Pivot

Signal harvested -> out-*; route named -> that skill.
