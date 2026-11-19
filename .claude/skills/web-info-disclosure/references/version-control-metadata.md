# VCS metadata beyond .git

.svn, .hg, .bzr and partial .git states each leak differently — different file layouts, different recovery paths.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.svn/entries or wc.db | SVN exposed | reconstruct from entries |
| /.hg/requires or .hg/store | Mercurial exposed | walk store |
| /.bzr/README or .bzr/branch-format | Bazaar | walk |
| partial .git: HEAD yes, objects no | refs only | report honestly |

## Steps

1. Probe /.svn/entries, /.svn/wc.db, /.hg/requires, /.bzr/README.
2. SVN: entries lists files + revisions; fetch pristine copies from .svn/text-base.
3. HG: walk .hg/store/data for revlog files.
4. Partial .git (refs but no objects): you have commit hashes and filenames only — record honestly, don't fabricate a tree.

## Falsifier

Falsifier — none of the VCS metadata paths return real metadata: no repository is exposed.

## Traps

- Modern SVN (1.7+) uses wc.db sqlite — fetch it and query locally.
- Partial recovery is still a finding: the filenames alone reveal structure.
- A .git with only pack files needs the pack protocol — git_dumper reports this honestly.

## Commands

```bash
for p in /.svn/entries /.svn/wc.db /.hg/requires /.git/HEAD; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`git-exposure.md` · `tools-git-dumper.md`
