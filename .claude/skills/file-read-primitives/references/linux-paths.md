# Linux Paths — the read corpus

## The identity/auth files — the credential corpus

```
/etc/passwd                — users (proof-of-read)
/etc/shadow                — password hashes (needs root-read)
/etc/group
/etc/gshadow
/etc/sudoers
/etc/sudoers.d/*
/etc/sudoers.d/50_*
/etc/security/opasswd
/etc/security/passwd
/etc/login.defs
/etc/pam.d/*
```

## The service configs — where the creds live

```
/etc/ssh/sshd_config       — ssh config
/etc/ssh/ssh_config
/root/.ssh/id_rsa
/root/.ssh/id_dsa
/root/.ssh/id_ecdsa
/root/.ssh/id_ed25519
/root/.ssh/authorized_keys
/root/.ssh/known_hosts
/home/*/.ssh/id_rsa
/home/*/.ssh/authorized_keys
/home/*/.ssh/config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/*.conf
/etc/nginx/sites-enabled/*
/etc/nginx/sites-available/*
/etc/apache2/apache2.conf
/etc/apache2/sites-enabled/*
/etc/apache2/sites-available/*
/etc/apache2/ports.conf
/etc/apache2/envvars
/etc/apache2/conf-enabled/*
/etc/apache2/mods-enabled/*
/etc/httpd/conf/httpd.conf
/etc/httpd/conf.d/*.conf
/etc/lighttpd/lighttpd.conf
/etc/caddy/Caddyfile
/etc/haproxy/haproxy.cfg
/etc/varnish/default.vcl
/etc/squid/squid.conf
/etc/postfix/main.cf
/etc/postfix/master.cf
/etc/dovecot/dovecot.conf
/etc/dovecot/conf.d/*
/etc/exim4/exim4.conf.template
/etc/sendmail.cf
/etc/dovecot/dovecot-sql.conf
/etc/openvpn/server.conf
/etc/wireguard/wg0.conf
/etc/resolv.conf
/etc/hosts
/etc/hostname
/etc/host.conf
/etc/network/interfaces
/etc/netplan/*.yaml
/etc/dhcp/dhclient.conf
/etc/NetworkManager/system-connections/*
/etc/sysconfig/network-scripts/ifcfg-*
```

## The app/framework configs

```
/var/www/html/.env
/var/www/html/.env.local
/var/www/html/.env.production
/var/www/html/config.php
/var/www/html/index.php
/var/www/html/wp-config.php
/var/www/html/configuration.php
/var/www/html/settings.php
/var/www/html/local_settings.py
/var/www/html/app.py
/var/www/html/main.py
/var/www/html/server.js
/var/www/html/app.js
/var/www/html/package.json
/var/www/html/composer.json
/var/www/html/composer.lock
/var/www/html/requirements.txt
/var/www/html/Pipfile
/var/www/html/Gemfile
/var/www/html/Gemfile.lock
/var/www/html/yarn.lock
/var/www/html/pnpm-lock.yaml
/var/www/html/go.mod
/var/www/html/Cargo.toml
/var/www/html/pom.xml
/var/www/html/build.gradle
/var/www/html/Dockerfile
/var/www/html/docker-compose.yml
/app/.env
/app/config.yml
/app/config.yaml
/app/config.json
/app/config.ini
/app/settings.py
/app/main.py
/app/app.py
/opt/app/config.ini
/opt/app/.env
/opt/app/config.yml
/home/ctf/.env
/home/ctf/config.yml
/home/ctf/.env.local
/home/ctf/app.py
```

## The DB configs

```
/etc/mysql/my.cnf
/etc/mysql/debian.cnf      — debian-sys-maint creds!
/etc/mysql/conf.d/*
/etc/mysql/mariadb.cnf
/etc/mysql/mysql.conf.d/*
/etc/postgresql/*/main/postgresql.conf
/etc/postgresql/*/main/pg_hba.conf
/etc/postgresql/*/main/pg_ident.conf
/etc/redis/redis.conf      — requirepass line
/etc/mongod.conf
/etc/mongodb.conf
/etc/memcached.conf
/etc/cassandra/cassandra.yaml
/etc/couchdb/local.ini
/etc/elasticsearch/elasticsearch.yml
/etc/kibana/kibana.yml
/etc/influxdb/influxdb.conf
/etc/rabbitmq/rabbitmq.conf
/etc/rabbitmq/definitions.json
/etc/kafka/server.properties
/etc/zookeeper/zoo.cfg
~/.my.cnf                  — user mysql creds
~/.pgpass                  — postgres creds
~/.mongorc.js
```

## The log files — the evidence corpus

```
/var/log/auth.log          — ssh/sudo auth
/var/log/secure            — auth on RHEL
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/httpd/access_log
/var/log/httpd/error_log
/var/log/syslog
/var/log/messages
/var/log/dmesg
/var/log/kern.log
/var/log/cron.log
/var/log/mail.log
/var/log/mail.err
/var/log/fail2ban.log
/var/log/ufw.log
/var/log/apt/history.log
/var/log/dpkg.log
/var/log/yum.log
/var/log/dnf.log
/var/log/wtmp              — login history (binary — strings)
/var/log/btmp              — failed logins
/var/log/lastlog
/var/log/faillog
/var/log/audit/audit.log
/var/log/journal/...        — systemd journal (binary)
/var/log/php-fpm/error.log
/var/log/php*-fpm/error.log
/var/log/supervisor/supervisord.log
/var/log/docker.log
/var/log/lfd.log
/var/log/btmp
/var/log/xferlog           — ftp
/var/log/proftpd/proftpd.log
/var/log/vsftpd.log
/var/log/mysqld.log
/var/log/postgresql/postgresql-*.log
/var/log/redis/redis-server.log
/var/log/mongodb/mongod.log
/var/log/cron
/var/log/anaconda/
/var/log/installer/
/var/log/unattended-upgrades/
```

## The shell-history corpus — where flags get typed

```
/root/.bash_history
/root/.zsh_history
/root/.mysql_history       — the mysql queries!
/root/.psql_history
/root/.sqlite_history
/root/.python_history
/root/.node_repl_history
/root/.viminfo
/root/.lesshst
/root/.wget-hsts
/root/.curlrc
/home/*/.bash_history
/home/*/.zsh_history
/home/*/.mysql_history
/home/*/.psql_history
/home/*/.python_history
/home/*/.viminfo
```

`.mysql_history` — the past queries — a `FLAG` literal in a SELECT
may be there.

## The cloud/k8s/docker secrets

```
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/var/run/secrets/kubernetes.io/serviceaccount/namespace
/run/secrets/*                       — docker secrets
/run/secrets/db_password
/run/secrets/redis_password
/var/lib/docker/containers/*/config.json
/var/lib/docker/image/*
/var/run/docker.sock                  — a socket, not a file
/root/.docker/config.json
/root/.aws/credentials
/root/.aws/config
/root/.kube/config
/root/.config/gcloud/application_default_credentials.json
/root/.azure/
/root/.gcp/
/root/.terraform.d/credentials.tfrc.json
/home/*/.aws/credentials
/home/*/.kube/config
```

## The backup/archive corpus

```
/root/backup.tar.gz
/root/backup.zip
/root/backups/*
/var/backups/*
/var/backups/*.tar.gz
/opt/backup/*
/tmp/backup/*
/home/*/backup*
/etc/cron.d/backup*
/var/lib/backuppc/
```

## The cron/systemd corpus

```
/etc/crontab
/etc/cron.d/*
/etc/cron.daily/*
/etc/cron.hourly/*
/etc/cron.weekly/*
/etc/cron.monthly/*
/var/spool/cron/crontabs/*
/var/spool/cron/*
/etc/systemd/system/*.service
/etc/systemd/system/*.timer
/usr/lib/systemd/system/*.service
/etc/init.d/*
/etc/rc.local
/etc/rc*.d/*
```

## The flag-file corpus — the CTF defaults

```
/flag
/flag.txt
/root/flag
/root/flag.txt
/home/ctf/flag
/home/ctf/flag.txt
/app/flag
/app/flag.txt
/var/flag
/var/flag.txt
/tmp/flag
/opt/flag
/run/flag
/srv/flag
/flag{...}
```
