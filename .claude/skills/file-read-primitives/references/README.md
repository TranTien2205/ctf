# File-Read Primitives — Reference Index

The canonical entry contract lives at `../SKILL.md`. This directory is
the depth corpus — each file is loadable on demand. Start with
`field-manual.md` for the ordered playbook or `payload-dictionary.md`
for the copy-paste corpus.

## Start here

- `../SKILL.md` — the canonical contract (first probe, falsifier, budget)
- `field-manual.md` — the ordered playbook (stages 0-11)
- `workflow.md` — the runbook (stages 0-10)
- `read-pipeline.md` — the escalation ladder, rung-order
- `detection.md` — the canary signals and the oracle-map
- `detection-oracle.md` — error-type → mechanism map
- `theory.md` — the boundary model — read/exec/oracle, schemes, joins, confines

## The payload corpus

- `payload-dictionary.md` — the traversal/read corpus by purpose (1.1k lines)
- `cheatsheet.md` — the pocket reference — first probes, ladders, corpus order
- `encoding-tricks.md` — UTF-8 overlong/fullwidth/Unicode separators, encoding layers

## The traversal/syntax surface

- `traversal-variants.md` — `..`, `...//`, `..//`, `..;/`, `%2e%2e%2f`, `%00`, etc.
- `traversal-and-wrappers.md` — the canonical SKILL.md's core traversal doc

## The per-stack surface

- `per-stack.md` — Java/Python/Node/Ruby/Go/.NET sinks, the `/WEB-INF` corpus
- `php-wrappers.md` — `php://`/`phar://`/`zip://`/`glob://`/`expect://`/`ssh2.*`/`data:`/`compress.*`/`filter` chains
- `url-wrapper-matrix.md` — every scheme, reads/execs/writes/listings

## The filesystem corpus

- `linux-paths.md` — the Linux path corpus — system, app, secrets, history, proc
- `windows-paths.md` — the Windows path corpus — system, app, IIS, user, powershell
- `proc-filesystem.md` — `/proc/self/*`, `/proc/N/*`, `/proc/net/*`, fds, mounts
- `container-world.md` — Docker/K8s/container — `/proc/1/environ`, secrets, sockets
- `flag-paths.md` — where the flag lives — env/file/source/db/log/git/backup
- `source-location.md` — finding the app's own files — the include-chain
- `secrets-and-keys.md` — the cred-corpus — ssh, cloud, db, api, ci, mail
- `extended-corpus.md` — `/sys`, `/dev`, the long-tail read surfaces
- `real-world-cases.md` — the patterns actual apps showed

## The read-sink surfaces

- `include-vs-read.md` — the sink-type map — read/exec/oracle
- `read-to-rce.md` — the RCE-ladders — `include`, `php://input`, `expect://`,
  `pearcmd`, `phar://`, `zip://`, `sess_`, `data:`, log-poison, fd, eval
- `log-poisoning.md` — the log-inject→include chain
- `archive-traversal.md` — `zip://`/`phar://`/`jar:`/`rar://`/`tar:` member-paths
- `archive-deep.md` — the archive-scheme family — `#`/`!` separators
- `blind-read.md` — `file_exists`/`filesize`/`md5_file`/`getimagesize`/
  `include-error`/`fd`/`timing` oracles
- `second-order.md` — the deferred-read shapes — stored/cron/event/async

## The confine/bypass surface

- `filter-bypass.md` — the byte/word-filter bypasses
- `denied-conditions.md` — `open_basedir`/`realpath`/`chroot`/`safe_join`/
  `MapPath`/`SecManager`/LSM/perm/mount walls
- `exploit-ladders.md` — the read→source→config→creds→exec→flag ladders

## The evidence/process surface

- `evidence-rules.md` — what counts as a read — verbatim-content rules
- `common-mistakes.md` — the budget-burners — reflection-vs-read, confine-vs-miss
- `ctf-shapes.md` — how file-read challenges actually appear
- `whitebox-hunt.md` — the grep-corpus per stack
- `tooling.md` — `lfi_probe`/`http_probe`/`read_loop`/`sanitizer_fuzz`/
  `oob_listener`/`hooks`/`state`/`decide`/`classify`/`chain_match`/
  `writeup_search`/`variant_matrix`/`selftest`/`id_sweep`/`gadget_lookup`
- `attack-defense.md` — the ad-contest file-read — `tools/ad/` chains
- `proc-and-source-enum.md` — the canonical proc+source doc
- `../field-notes.md` — the local-verified notes
