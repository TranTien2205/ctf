# Path enum: gitvariants

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Exposed VCS probing order: /.git/HEAD (ref:
line = full tree downloadable), /.git/config (remote URL leak),
/.gitignore, /.git/description, /.svn/entries, /.hg/, /.bzr/.
A 200 on HEAD means tools/git-dumper territory - the source is
recoverable = infodisclosure finding material, recorded
verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
