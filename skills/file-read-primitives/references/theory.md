# Theory — what a file-read primitive actually is

## The boundary — who controls the path

A file-read primitive exists when untrusted input reaches a path-
consuming syscall unfiltered. The boundary is the path: your input
decides WHICH file the server opens.

## The three shapes — read, exec, oracle

- **read** — `file_get_contents`/`readfile`/`open`/`fs.readFile` — the
  file's bytes come back
- **exec** — `include`/`require`/`load`/`require()`/`eval(content)` —
  the file's bytes are PARSED as code
- **oracle** — `file_exists`/`filesize`/`md5_file`/`getimagesize` —
  the file's EXISTENCE/METADATA leaks

The sink TYPE decides which primitive you have — `include-vs-read.md`.

## The normalization boundary — where traversal lives

`..`/`./`/`//`/`\`/`%2e`/`%2f`/`%5c`/overlong/fullwidth — the path
string is a grammar, normalization is the parse — traversal is a
normalization exploit — the app joins `base + input` and resolves —
`../../` resolves out.

## The scheme boundary — where wrappers live

`file://`/`php://`/`phar://`/`zip://`/`glob://`/`expect://`/`data:`/
`jar:`/`netdoc:`/`http://`/`ftp://`/`ssh2.*` — a URL has a scheme —
the scheme selects a HANDLER — `file_get_contents` takes a URL —
`php://filter` is a URL that reads locally — the wrapper is a scheme-
handler the app's fetch doesn't distinguish from `http://`.

## The authority boundary — `file:///` vs `file://`

`file:///x` = empty-authority + `/x` path. `file://localhost/x`/`file://
127.0.0.1/x` = authority-checked-sometimes. `file://attacker/x` = remote
— the authority is the remote/local decision-point.

## The join-boundary — where `base` + `input` lives

- `join("/app", "/etc/passwd")` = `/etc/passwd` — absolute REPLACES —
  Python/Node `path.join` quirk
- `join("/app", "../../etc/passwd")` = `/app/../../etc/passwd` —
  resolve-time traversal
- `"/app/" + input` = `/app/../../etc/passwd` — concat-time traversal

The join-manner is the traversal's lever.

## The resolve-boundary — realpath/normalize/abspath

`realpath`/`normpath`/`abspath`/`canonicalize` — the resolve-step —
a `..` inside a `join`'d path resolves out at resolve-time — the
confine-check must happen AFTER resolve or the traversal wins.

## The confine-boundary — the check that decides

- `startswith(base)` on the resolved path
- `is_relative_to(base)` modern
- `open_basedir` PHP
- `realpath + startswith`
- `SecurityManager.checkRead` Java

The confine is a check AFTER resolve — the check's exact expression
is the bypass target.

## The fd-boundary — the fd-as-file

`/proc/self/fd/N`/`/dev/fd/N`/`/dev/std*` — an fd is a file — the
fd-number is the path — a path that names an fd reads the fd's target —
the fd-namespace as filesystem.

## The proc-boundary — `/proc` as the self-view

`/proc/self/*` — the process views itself — `environ`/`cmdline`/`cwd`/
`exe`/`maps`/`mountinfo`/`fd/*`/`root` — the procfs is a filesystem
view of the process's own state — the read-recon engine.

## The memory-boundary — `/proc/self/mem` + `maps`

`/proc/self/maps` + `/proc/self/mem` — the process's address-space as
files — `maps` names the regions, `mem` reads them — the memory-read
primitive.

## The archive-boundary — inside-archive paths

`zip://x.zip#member`/`phar://x.phar/a`/`jar:x.jar!/a`/`rar://x.rar#a` —
the `#`/`!` splits the archive-path from the member-path — the archive
is a filesystem inside a file.

## The stream-boundary — `php://filter` chains

`php://filter/A|B|C/resource=x` — filters compose — `convert.base64-encode`/
`zlib.deflate`/`iconv`/`string.rot13`/`dechunk` — the stream-filter is
a transform-pipeline applied to the file's bytes.

## The cookie/session boundary — `sess_*` as a file

`/tmp/sess_<id>` — the session is a FILE — `file_get_contents` reads it
— `include` execs it — the session-file as a read/exec surface.

## The log boundary — the log-as-a-file

`/var/log/*` — logs are files — `file_get_contents` reads them —
`include` execs them — log-poisoning = write-to-log + include-log —
`log-poisoning.md`.

## The "the read is an oracle too" — the many shapes of a read

- full-content echo — the in-band read
- no echo + status diff — the status-oracle
- no echo + error diff — the error-oracle
- no echo + timing diff — the timing-oracle
- hash/meta echo — the meta-oracle
- include-error — the parse-oracle
- a listing — the dir-oracle
- an fd — the fd-oracle

A read primitive's channel varies — `blind-read.md` for the non-echo
cases.

## The "the read is the reach" — the reach-model

A read primitive's VALUE is its REACH — which files it can open —
the perm-set (`Uid`/`Gid`), the confine (`open_basedir`/`realpath`/
`chroot`), and the mount-set (`/proc`/`/dev`/`/sys`/binds) bound the
reach — the flag must live inside the reach.

## The "the read is a primitive, not a chain" — the mechanism-boundary

The READ is the mechanism — the CHAIN is source→config→creds→exec→flag
— `exploit-ladders.md` — don't confuse the primitive (the read works)
with the chain (the read leads to impact).

## The "the read is the weakest-signal-verified" — the confirm-standard

A `file_exists` oracle confirms "a path resolves" — a `file_get_contents`
echo confirms "the content came back" — the verbatim-content-echo is
the gold-standard — `evidence-rules.md`.
