# VCS metadata beyond .git — case catalogue

.svn, .hg, .bzr and partial .git states each leak differently — different file layouts, different recovery paths.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.svn/entries or wc.db | SVN exposed | reconstruct from entries |
| 2 | /.hg/requires or .hg/store | Mercurial exposed | walk store |
| 3 | /.bzr/README or .bzr/branch-format | Bazaar | walk |
| 4 | partial .git: HEAD yes, objects no | refs only | report honestly |

## Falsifier

Falsifier — none of the VCS metadata paths return real metadata: no repository is exposed.

## Coverage notes

- Modern SVN (1.7+) uses wc.db sqlite — fetch it and query locally.
- Partial recovery is still a finding: the filenames alone reveal structure.
- A .git with only pack files needs the pack protocol — git_dumper reports this honestly.

## Cross-references

`git-exposure.md` · `tools-git-dumper.md`
