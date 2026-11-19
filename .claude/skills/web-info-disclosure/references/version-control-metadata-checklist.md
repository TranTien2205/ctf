# VCS metadata beyond .git — operational checklist

.svn, .hg, .bzr and partial .git states each leak differently — different file layouts, different recovery paths.

## Checklist

- [ ] Probe /.svn/entries, /.svn/wc.db, /.hg/requires, /.bzr/README.
- [ ] SVN: entries lists files + revisions; fetch pristine copies from .svn/text-base.
- [ ] HG: walk .hg/store/data for revlog files.
- [ ] Partial .git (refs but no objects): you have commit hashes and filenames only — record honestly, don't fabricate a tree.

## Abort conditions

- Modern SVN (1.7+) uses wc.db sqlite — fetch it and query locally.
- Partial recovery is still a finding: the filenames alone reveal structure.
- A .git with only pack files needs the pack protocol — git_dumper reports this honestly.

## Falsifier

Falsifier — none of the VCS metadata paths return real metadata: no repository is exposed.

## Cross-references

`git-exposure.md` · `tools-git-dumper.md`
