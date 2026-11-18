# OS Differences — Linux / macOS / BSD / Solaris / AIX / Windows

## The shell differences — `shell-differences.md` covers sh-vs-cmd; this is the OS layer

| OS | Default shell | Path | Notes |
|---|---|---|---|
| Linux | sh→dash/bash | `/bin/sh` `bash` | GNU coreutils |
| macOS | zsh→bash | `/bin/zsh` `/bin/sh` | BSD userland |
| FreeBSD | sh→csh | `/bin/sh` | BSD userland |
| OpenBSD | ksh | `/bin/ksh` `/bin/sh` | pdksh |
| Solaris | sh | `/usr/bin/sh` | POSIX-sh |
| AIX | ksh | `/usr/bin/ksh` | Korn |
| HP-UX | sh | `/usr/bin/sh` | POSIX |
| Windows | cmd | `cmd.exe` `powershell` | NT |

## The userland-difference — the same command name, different flags

| Command | GNU/Linux | BSD/macOS |
|---|---|---|
| `ps` | `ps aux` | `ps aux` — same but different columns |
| `netstat` | `-tulpn` | `-an`/`netstat -rn` |
| `sed -i` | `-i` alone | `-i ''` — macOS needs empty arg |
| `stat` | `-c` | `-f` |
| `date -d` | GNU `-d` | BSD `-j`/`-v` |
| `find` | `-printf` | no `-printf` |
| `xargs` | `-r`/`--no-run-if-empty` | no `-r` |
| `tar` | `-I`/`--use-compress-program` | `-I`/`--use-compress-program` |
| `tail` | `-n +N`/`+N` | same |
| `head` | `-n N` | same |
| `wc` | `-l` | same |
| `ls` | `-la`/`--color` | `-la`/`/G` color |
| `cp` | `-r` | same |
| `mv` | `-f` | same |
| `rm` | `-r` | same |
| `id` | `id` | `id` |
| `whoami` | `whoami` | `whoami` |
| `hostname` | `hostname`/`hostname -f` | same |
| `uname` | `-a` | same |
| `which` | `which`/`command -v`/`type` | `which`/`whereis` |
| `whereis` | `whereis` | `whereis` |
| `locate` | `locate` | `locate` |
| `grep` | `-r` | `-r` |
| `awk` | `gawk`-features | `nawk`/`awk` — fewer |
| `nc` | `-e`/`nc.traditional`/`ncat` | `nc -e`? BSD `nc` has `-e`? no — OpenBSD `nc` removed `-e` |
| `nc`/`netcat`/`ncat`/`socat`/`nc.openbsd`/`nc.traditional` | variants | variants |
| `base64` | `-d` | `-D`? — BSD uses `-D`/`-b` |
| `xxd` | `-p` | same |
| `od` | `-A n -t x1` | same |
| `hexdump` | `-C` | same |
| `script` | `-qc`/`/dev/null` | `-q /dev/null` |
| `script` | `-c 'cmd' file` | `file` arg-position |
| `timeout` | `timeout N cmd` | `gtimeout`/absent on macOS |
| `stdbuf` | `-o0` | absent |
| `flock` | `flock file cmd` | absent |
| `watch` | `-n` | absent |
| `readlink` | `-f` | `-f`? macOS `readlink` no `-f` |
| `realpath` | `realpath` | absent on some |
| `mktemp` | `-d` | `-d` same but `-t` differs |
| `install` | `-D` | `-d` |
| `openssl` | same | same |
| `certutil` | absent | absent (win) |
| `wget`/`curl` | both | macOS ships `curl` not `wget` |
| `python` | `python3`/`python` | `python3` |
| `perl` | `perl` | `perl` |
| `ruby` | `ruby` | `ruby` (system on macOS) |
| `php` | `php` | absent |
| `node` | `node` | absent |
| `lua` | `lua` | absent |

## The `/bin`/`/sbin`/`/usr/bin`/`/usr/sbin`/`/usr/local/bin`/`/opt` paths — where binaries live

- Linux: `/bin`→`/usr/bin` symlink, `/sbin`→`/usr/sbin`
- macOS: `/bin` `/usr/bin` `/usr/local/bin` `/opt/homebrew/bin` (ARM)
- BSD: `/bin` `/usr/bin` `/usr/local/bin` `/usr/pkg/bin`
- Solaris: `/usr/bin` `/usr/sbin` `/usr/ucb` `/usr/sfw/bin`
- AIX: `/usr/bin` `/usr/sbin` `/usr/local/bin` `/opt/freeware/bin`

The glob-paths: `/???/cat`/`/???/id`/`/??n/cat`/`/usr/???/cat`/`/b*/cat`.

## The flag-file locations — the OS-specific paths

```
Linux:   /flag /flag.txt /root/flag /home/*/flag /app/flag*
         /proc/1/environ /proc/self/environ
         /etc/flag /srv/flag /opt/flag /var/flag /tmp/flag
macOS:   /flag /Users/*/flag /private/tmp/flag
         /var/root/flag /etc/flag
BSD:     /flag /root/flag /home/*/flag /etc/flag /tmp/flag
Windows: c:\flag.txt c:\flag c:\users\*\flag.txt
         c:\windows\flag c:\temp\flag
         %USERPROFILE%\flag.txt %TEMP%\flag %PROGRAMDATA%\flag
```

## The service/scheduled-task equivalents — the persistence paths

```
Linux:    /etc/crontab /etc/cron.d /var/spool/cron systemd units
macOS:    ~/Library/LaunchAgents /Library/LaunchDaemons launchd plists
BSD:      /etc/crontab /var/cron/tabs /etc/rc.local
Windows:  schtasks /Scheduled Tasks/ %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup registry Run keys services
```

## The `/proc`/`/sys` — Linux-only special-fs

```
/proc/self/environ      — process env
/proc/1/environ         — init env
/proc/self/cmdline
/proc/self/status
/proc/self/maps
/proc/net/tcp|udp|tcp6|udp6
/proc/mounts
/proc/version
/proc/cpuinfo
/proc/meminfo
/proc/sys/kernel/hostname
/sys/class/dmi/id/product_name
/sys/class/net/*/address
/sys/block/*/device/model
/sys/firmware/efi/efivars
```

## Windows-side — `windows-cmdi.md`/`powershell-injection.md` detail

The cmd/ps/`certutil`/wmic/`schtasks`/`sc`/`reg`/`net`/`netsh`/`ipconfig`/
`whoami`/`hostname`/`ver`/`systeminfo`/`tasklist`/`taskkill`/`wmic`/
`powershell`/`pwsh`/`bitsadmin`/`certutil`/`curl`/`mshta`/`rundll32`/
`regsvr32`/`regsvcs`/`msbuild`/`csc`/`vbc`/`installutil`/`msxsl`/`forfiles`/
`pcalua`/`cmstp`/`msiexec`/`odbcconf`/`control`/`desk.cpl`/`mavinject`/
`presentationhost`/`xwizard`/`syncappvpublishingserver`/`ieexec`/`dfsvc`/
`dfsutil`/`aspnet_compiler`/`jsc`/`vsi`/`cl`/`tracker`/`vstest.console`/
`defaultpack`/`fsutil`/`esentutl`/`expand`/`extrac32`/`makecab`/`msbuild`/
`msconfig`/`netsh`/`rasautou`/`rasdial`/`rassrv`/`sdbinst`/`diantz`/
`diskshadow`/`dnscmd`/`excel`/`winword`/`powerpnt`/`msaccess`/`mspub`/
`visio`/`msproject`/`wscript`/`cscript`/`wmic`/`mshta`/`rundll32`/
`regsvr32`/`msbuild`/`csc`/`vbc`/`installutil`/`regasm`/`regsvcs`/`jsc`/
`vsi`/`aspnet_compiler`/`tracker`/`vstest`/`workfolders`/`excel`/`word`/
`powerpoint`/`access`/`publisher`/`visio`/`project`/`onenote`/`lync`/
`skype`/`teams`/`zoom`/`slack`/`discord`/`electron`/`cef`/`chrome`/`edge`/
`firefox`/`safari`/`opera`/`brave`/`vivaldi`/`tor`/`iexplore`/`msedge` —
the Windows-side toolbox.

## The BSD/Solaris/AIX specifics — the rare-userland shapes

- `nc` — OpenBSD's `nc` removed `-e` — `nc -l`/`nc x p` still work
- `awk` — BSD `awk`/`nawk` lacks some `gawk` features — `awk 'BEGIN{system("id")}'` still works
- `sed` — BSD `sed` has no `e` command — GNU `sed`'s `s/x/e cmd/e` won't work
- `tar` — BSD `tar`/`bsdtar`/`libarchive` — `--checkpoint-action` is GNU
- `find` — BSD `find` has `-exec`/`-ok` same but no `-fprintf`/`-fls`
- `stat` — BSD `-f` format-string, GNU `-c`
- `date` — BSD `-j`/`-v` vs GNU `-d`
- `xargs` — BSD no `-r`
- `timeout` — BSD absent — `perl -e alarm`/`python` workarounds
- `script` — BSD `script -q /dev/null` — no `-c`
- `md5`/`sha256` — BSD command names vs `md5sum`/`sha256sum` GNU
- `base64` — BSD `-D` decode vs GNU `-d`
- `openssl` — same both sides
- `grep` — BSD `-r` same but `-P` differs
- `sort` — BSD lacks `-R` random-sort
- `shuf` — BSD absent — `jot`/`awk`/`perl` for shuffle
- `seq` — BSD has `jot` instead
- `fmt`/`fold` — both
- `tr` — same
- `nl` — same
- `pr` — same
- `expand`/`unexpand` — same
- `paste` — same
- `join` — same
- `comm` — same
- `cut` — same
- `split` — `-n` differs (BSD `-n chunks` vs GNU)
- `csplit` — differs
- `tac` — BSD absent — `tail -r`
- `rev` — same
- `shuf`/`jot`/`random` — different
- `uuidgen` — macOS has it, linux `cat /proc/sys/kernel/random/uuid`
- `uuid` — varies
- `sw_vers`/`sysctl`/`system_profiler`/`defaults`/`plutil`/`launchctl`/`launchd`/`dscl`/`dscacheutil`/`dsconfigad`/`dseditgroup`/`dsmemberutil`/`pwpolicy`/`sysadminctl`/`fdesetup`/`hdiutil`/`diskutil`/`apfs`/`nvram`/`pmset`/`caffeinate`/`mdfind`/`mdls`/`mdutil`/`mdimport`/`xcode-select`/`xcrun`/`xcodebuild`/`codesign`/`spctl`/`sfltool`/`security`/`osascript`/`automation`/`automator`/`shortcuts`/`open`/`pbcopy`/`pbpaste`/`say`/`screencapture`/`screencapture`/`qlmanage`/`textutil`/`afinfo`/`afconvert`/`afplay`/`avconvert`/`drutil`/`hdiutil`/`asr`/`bless`/`installer`/`pkgutil`/`productbuild`/`productsign`/`pkgbuild`/`xar`/`bom`/`lsbom`/`kbsexec`/`kextload`/`kextunload`/`kextstat`/`kextutil`/`kmutil`/`systemextensionsctl`/`networksetup`/`airport`/`systemsetup`/`sharing`/`remote`/`kickstart`/`screen`/`sips`/`lp`/`lpstat`/`lpadmin`/`cupsd`/`cupsctl`/`launchctl`/`log`/`sysdiagnose`/`spindump`/`sample`/`heap`/`leaks`/`malloc_history`/`fs_usage`/`sc_usage`/`latency`/`top`/`powermetrics`/`taskinfo`/`vm_stat`/`memory_pressure`/`purge`/`purgeable`/`dynamic_pager`/`swap`/`nvram`/`nvram`/`nvram`/`csrutil`/`spctl`/`tccutil`/`sqlite3`/`plutil`/`defaults`/`PlistBuddy`/`plutil`/`cfprefsd`/`distnoted`/`cfprefsd`/`ubd`/`cloudd`/`bird`/`nsurlsessiond`/`nsurlstoraged`/`appstoreagent`/`storeaccountd`/`akd`/`authd`/`secinitd`/`securityd`/`Keychain`/`login`/`logind`/`securityd`/`cfprefsd`/`notifyd`/`distnoted`/`opendirectoryd`/`mds`/`mdworker`/`mds_stores`/`fseventsd`/`diskarbitrationd`/`configd`/`networkserviceproxy`/`mDNSResponder`/`awdd`/`symptomsd`/`adprivacyd`/`rapportd`/`blued`/`airportd`/`wifid`/`locationd`/`nearbyd`/`sharingd`/`useractivityd`/`nsurlsessiond`/`apsd`/`imagent`/`identityservicesd`/`callhistoryd`/`SMS`/`iMessage`/`FaceTime`/`screensharingd`/`ARDAgent`/`RemoteManagement`/`AppleVNCServer`/`lockdownd`/`usbmuxd`/`MobileBackup`/`diagnosticd`/`sysdiagnose`/`ReportCrash`/`asl`/`syslogd`/`logd`/`diagnosticd`/`jetsam`/`memorystatus`/`backboardd`/`SpringBoard`/`CommCenter`/`lockdownd`/`installd`/`online-auth-agent`/`webinspectord`/`securityd`/`keybagd`/`mobileactivationd`/`fairplayd`/`keybagd`/`profiled`/`misd`/`afcd`/`mobile_installation_proxy`/`com.apple.mobilebackup`/`com.apple.afc` — macOS/darwin-side toolbox (deep enough that only the relevant ones matter)

## The "the binary is there but the flag differs" cheat-table

| Task | GNU/Linux | BSD/macOS |
|---|---|---|
| recursive grep | `grep -r` | `grep -r` |
| find+exec | `find . -exec` | same |
| sed in-place | `sed -i ''` on macOS | `sed -i` on GNU |
| base64-decode | `base64 -d` | `base64 -D` macOS, `-d` BSD |
| md5 | `md5sum` | `md5`/`md5 -q` |
| sha256 | `sha256sum` | `shasum -a 256`/`sha256` |
| stat | `stat -c %s` | `stat -f %z` |
| date-parse | `date -d 'x'` | `date -j -f` |
| read-file-into-args | `xargs -a f` | `xargs < f`/`xargs -J` |
| no-run-if-empty | `xargs -r` | no `-r` |
| no-run-if-empty | `xargs --no-run-if-empty` | absent |
| timeout | `timeout N` | `gtimeout`/absent |
| seq | `seq 1 10` | `jot 10 1` |
| random-lines | `shuf` | `jot -r`/awk |
| read-file-as-arg | `xargs -a f` | `xargs < f` |
| tac | `tac` | `tail -r` |
| script-replay | `script -qc` | `script -q file cmd` |
| stdbuf | `stdbuf -o0` | absent |
| flock | `flock` | absent |
| realpath | `realpath` | `realpath`/`readlink -f`? macOS no `-f` |
| readlink | `readlink -f` | `readlink` (no -f) |
| mktemp-dir | `mktemp -d` | `mktemp -d` |
| install-dir | `install -d` | same |
| install-file | `install src dst` | same |

## The "I don't know which OS" fingerprint probes

```
uname -a                    — Linux/Darwin/FreeBSD/SunOS/AIX/HP-UX
cat /etc/os-release         — linux-only
uname -s                    — kernel-name
ls /proc                    — /proc exists → linux
ls /System                  — darwin
cat /etc/release            — solaris
oslevel                     — aix
uname -M                    — aix model
prtconf | head              — solaris
sw_vers                     — macos
sysctl kern.version         — bsd/macos
sysctl hw.model             — bsd/macos
```

## Output to record

- which OS + which command-variant worked
