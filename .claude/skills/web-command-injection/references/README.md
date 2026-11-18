# web-command-injection — reference index

Canonical contract: `../SKILL.md`. This index routes each question to one
module. The class boundary (verified by chain card): code reaching an
**evaluator** — `eval()`, an expression sandbox, a calculator — is the same
finding as a metacharacter reaching a shell.

## Decision tree

```
input reaches a sink?
├─ argv element, never a shell        → FALSIFIED (this class closed)
├─ shell string (system/popen/sh -c)  → separators.md + quoting.md
├─ eval()/expression evaluator        → eval-injection.md
├─ argv element but flag-position     → argument-injection.md
└─ unknown                            → detection.md first

filter blocks characters?
├─ no spaces          → char-restriction.md ($IFS, ${IFS}, tabs, braces)
├─ no /               → char-restriction.md (cd + relative, ${PATH:0:1})
├─ keyword blacklist  → keyword-filter.md (quoting, globbing, concat)
├─ alnum-only         → char-restriction.md + variable-tricks.md
└─ WAF/regex          → waf-bypass.md

output in response?
├─ yes → in-band extraction: data-exfil-channels.md
└─ no  → blind-cmdi.md → oob-exfil.md (DNS/HTTP/ICMP)

which shell?
└─ shell-differences.md → windows-cmdi.md / powershell-injection.md

which language sink?
└─ php-sinks / python-sinks / node-sinks / ruby-sinks / java-sinks /
   perl-sinks / golang-sinks
```

## Detection and confirmation

| File | Covers |
|---|---|
| `detection.md` | sink discovery, shell boundary, channel matrix |
| `detection-contexts.md` | where cmdi hides: params, headers, names, cron |
| `detection-sequences.md` | the ordered probe sets — 10-probe classify, fingerprint, channel, filter-map |
| `contexts.md` | the injection-surface taxonomy — shell-string/argv/eval/filename |
| `injection-points.md` | where the input lands — params/body/header/cookie/path/array |
| `injection-vectors.md` | field-by-field payload catalog per transport |
| `separators.md` | `;` `&` `|` `&&` `||` `\n` `$()` semantics per shell |
| `quoting.md` | closing quotes, nested quoting, absorbing trailing text |
| `inline-exec.md` | `$()` backticks subshells arithmetic |
| `shell.md` | the POSIX metachar deep-dive — operators, expansions, quoting |
| `error-analysis.md` | shell/quoting errors as signals per shell |
| `evidence-rules.md` | what confirms vs what stays inconclusive |
| `common-mistakes.md` | traps that burn budget |

## Blind and exfil

| File | Covers |
|---|---|
| `blind-cmdi.md` | timing channels, error-oracle, boolean cmdi |
| `oob-exfil.md` | DNS/HTTP/ICMP/smb exfil, oob_listener usage |
| `data-exfil-channels.md` | in-band, timing, error, length, port-knock |

## Bypasses

| File | Covers |
|---|---|
| `filter-bypass.md` | blacklist evasion survey |
| `regex-filters.md` | pattern-by-pattern bypass — anchors, modifiers, whitelists |
| `char-restriction.md` | no space/slash/alnum-only escapes |
| `letter-filter-shell.md` | letter-filtered eval — `~`/XOR/`++` byte-building (pcalc card) |
| `escapeshell-bypasses.md` | escapeshellarg/escapeshellcmd/addslashes — what each leaves |
| `keyword-filter.md` | blocked command names, tokenization breaks |
| `wildcard-globbing.md` | `/?/?` glob expansions replacing names |
| `variable-tricks.md` | `$IFS`, `${PATH:0:1}`, `${HOME:0:1}`, braces, `$@` |
| `encoding.md` | base64/hex/octal/rev decoding in-line |
| `waf-bypass.md` | WAF signatures and evasion patterns |

## Sink semantics per language

| File | Covers |
|---|---|
| `popen-system-exec.md` | which API reaches a shell and why |
| `exec-family.md` | the per-language exec API catalog — shell vs argv vs eval |
| `php-sinks.md` | system/exec/shell_exec/passthru/backticks/proc_open/eval |
| `php-deep.md` | PHP sink-by-sink reference + stream wrappers + callables |
| `python-sinks.md` | os.system, subprocess shell=True, eval/exec |
| `node-sinks.md` | exec/execSync vs execFile/spawn boundary |
| `ruby-sinks.md` | system/`/exec/IO.popen/Open3 |
| `java-sinks.md` | Runtime.exec tokenization, ProcessBuilder, scripting |
| `perl-sinks.md` | system/backticks/open pipe/IPC::Open3 |
| `golang-sinks.md` | exec.Command sh -c, syscall |
| `eval-injection.md` | eval(), expression languages, calculators (chain-card widening) |

## Shells

| File | Covers |
|---|---|
| `shell-differences.md` | sh/dash/bash/zsh/fish semantics that matter |
| `os-differences.md` | Linux/macOS/BSD/Solaris/Windows userland + flag paths |
| `windows-cmdi.md` | cmd.exe separators, quoting, builtins |
| `powershell-injection.md` | PS payloads, IEX, enc commands |
| `sandboxed-shells.md` | restricted PATH, chroot, rbash escapes |
| `restricted-shell.md` | rbash/lshell/rzsh/jailshell escapes per allowed binary |

## Escalation and context

| File | Covers |
|---|---|
| `argument-injection.md` | tar --checkpoint-action, find -exec, curl -o, option injection |
| `arg-injection-deep.md` | per-binary flag/exec table — find/tar/git/curl/ssh/nmap/langs |
| `argument-order.md` | getopt quirks, `--` separator, argv[0] tricks |
| `env-var-injection.md` | LD_PRELOAD, PATH, PYTHONPATH, IFS via env |
| `redirection-tricks.md` | `>`/`>>`/tee writes, config overwrite |
| `second-order.md` | stored cmdi: logs, filenames, db fields |
| `log-poisoning.md` | log entries reaching shell |
| `filename-injection.md` | filenames reaching shell commands |
| `imagemagick-deep.md` | convert/identify/mogrify — coders, delegates, MSL, policy |
| `common-tools-sinks.md` | ping/dig/convert/ffmpeg/git/exiftool wrappers |
| `chains.md` | cmdi → privesc/read/pivot chains |
| `os-level.md` | privesc ladder, flag hunt, /proc reads, container escape |
| `ssti-vs-cmdi.md` | boundary discrimination with template injection |
| `polyglot-payloads.md` | multi-shell single payloads |
| `denied-conditions.md` | falsifier catalogue |
| `ctf-shapes.md` | ping/traceroute/img-tools/network-tool challenge shapes |
| `workflow.md` | bounded end-to-end loop |
| `tooling.md` | cmdi_probe + hooks usage |
| `cheatsheet.md` | compressed field tables |
| `payload-dictionary.md` | full payload corpus by class |
| `whitebox-hunt.md` | grep patterns per language |
| `extended-corpus.md` | exotic and historical vectors |
| `writeup-techniques.md` | techniques harvested from solved writeups |
| `../field-notes.md` | local confirmed notes |
