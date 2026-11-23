# Path enum: backupnames

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Backup-name probes per discovered file:
index.php~ index.php.bak index.php.swp index.php.old index.orig
.save .backup; archive shapes backup.zip www.zip site.tar.gz
db.sql dump.sql. A .swp/.~ is vim-recoverable source. Bounded
to files already discovered - not a blind wordlist.
## Pivot

Signal harvested -> out-*; route named -> that skill.
