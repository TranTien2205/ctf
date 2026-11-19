# VCS metadata beyond .git — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.svn/entries or wc.db | SVN exposed | reconstruct from entries |
| /.hg/requires or .hg/store | Mercurial exposed | walk store |
| /.bzr/README or .bzr/branch-format | Bazaar | walk |
| partial .git: HEAD yes, objects no | refs only | report honestly |

## Falsifier

Falsifier — none of the VCS metadata paths return real metadata: no repository is exposed.
