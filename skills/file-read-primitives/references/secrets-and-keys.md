# Secrets & Keys — the read targets that chain to more access

## The credential corpus — what a read buys you

A file-read primitive's biggest value is often not the flag file — it
is the credentials that unlock the next layer.

## SSH keys — the shell chain

```
/root/.ssh/id_rsa
/root/.ssh/id_ed25519
/root/.ssh/id_ecdsa
/root/.ssh/id_dsa
/root/.ssh/authorized_keys         — which keys are trusted
/root/.ssh/known_hosts             — where this box connects
/home/*/.ssh/id_rsa
/home/*/.ssh/id_ed25519
/home/*/.ssh/config                — host aliases, jump hosts
/etc/ssh/ssh_config
/etc/ssh/sshd_config               — auth policy, PermitRootLogin
/etc/ssh/ssh_host_*_key            — HOST keys — impersonation, MITM
```

A private `id_rsa`/`id_ed25519` read → `ssh -i key user@host` — the
read becomes a shell. `sshd_config` reveals `PasswordAuthentication`,
`PermitRootLogin`, `AllowUsers` — the auth policy.

## Cloud credentials — the metadata-adjacent chain

```
/root/.aws/credentials             — [default] aws_access_key_id
/root/.aws/config
/home/*/.aws/credentials
/root/.azure/credentials
/root/.azure/accessTokens.json
/root/.azure/msal_token_cache.json
/home/*/.config/gcloud/credentials.db
/home/*/.config/gcloud/application_default_credentials.json
/root/.config/gcloud/*
/root/.kube/config                 — kubeconfig — cluster admin often
/home/*/.kube/config
/root/.docker/config.json          — registry auth — base64 creds
/home/*/.docker/config.json
/root/.docker/config.json + auth   — docker login base64
```

`.aws/credentials` → `aws sts get-caller-identity` → cloud access.
`.kube/config` → `kubectl` → cluster exec → other pods' flags.

## Database credentials — the SQLi chain

```
/var/www/html/wp-config.php        — DB_NAME/DB_USER/DB_PASSWORD
/app/config/database.yml           — rails
/app/.env                          — DATABASE_URL
/etc/mysql/my.cnf
/root/.my.cnf                      — mysql client creds — auto-login!
/root/.pgpass                      — postgres creds
/home/*/.pgpass
/var/lib/pgsql/data/pg_hba.conf
/etc/postgresql/*/main/pg_hba.conf
/root/.mongorc.js
/etc/mongod.conf
/etc/redis/redis.conf              — requirepass
/etc/memcached.conf
/etc/couchdb/local.ini
/var/www/html/sites/default/settings.php   — drupal
/app/storage/logs/laravel.log
/app/.env                          — laravel DB_*, APP_KEY
```

`.my.cnf` → `mysql` auto-login without `-p`. `.pgpass` → `psql` auto-login.
`APP_KEY` in laravel `.env` → session forgery + deser chains.

## App secrets — the forge chain

```
/app/.env — APP_KEY, JWT_SECRET, SESSION_SECRET, SECRET_KEY_BASE
/app/config/secrets.yml            — rails secret_key_base
/app/config/master.key             — rails encrypted credentials key
/app/config/credentials.yml.enc    — decrypt with master.key
/app/config/initializers/secret_token.rb
/var/www/html/config.php           — SECRET_KEY, AUTH_KEY (wordpress)
/var/www/html/wp-config.php        — AUTH_KEY, SECURE_AUTH_KEY, NONCE_*
```

`secret_key_base` → forge rails sessions. `JWT_SECRET` → sign your own
JWT. `APP_KEY` → laravel deser (`web-deserialization`). WordPress
`AUTH_KEY`/`NONCE_KEY` → session forgery.

## API tokens — the service chain

```
/root/.config/hub                  — github token
/home/*/.config/gh/hosts.yml       — gh CLI token
/root/.git-credentials             — https creds — user:pass
/home/*/.git-credentials
/root/.netrc                       — ftp/http creds
/home/*/.netrc
/etc/netrc
/root/.token
/app/.env — STRIPE_KEY, SENDGRID, SLACK_TOKEN
/app/config.json — api_key fields
/etc/gitlab/gitlab-secrets.json
/etc/gitlab/gitlab.rb
```

`.netrc` → ftp/http auto-login. `.git-credentials` → repo access →
source history → more flags.

## CI/CD secrets — the pipeline chain

```
/app/.gitlab-ci.yml                — variables may embed creds
/app/.github/workflows/*.yml       — secrets.GITHUB_TOKEN refs
/app/Jenkinsfile
/var/lib/jenkins/credentials.xml
/var/lib/jenkins/secrets/initialAdminPassword
/var/lib/jenkins/config.xml
/home/jenkins/credentials.xml
/root/.jenkins/credentials.xml
```

`initialAdminPassword` → jenkins admin → script console → exec.
`credentials.xml` + `secrets/master.key` + `hudson.util.Secret` →
decrypt CI secrets.

## Web-server secrets — the TLS chain

```
/etc/nginx/ssl/*.key
/etc/letsencrypt/live/*/privkey.pem
/etc/ssl/private/*.key
/root/*.pem
/app/certs/*.key
```

A TLS key read → MITM potential (usually out of scope) → but also
evidence of the app's own config layout.

## Mail secrets — the reset chain

```
/app/.env — MAIL_PASSWORD, MAILGUN_KEY
/etc/postfix/main.cf
/etc/exim4/passwd.client
/root/.muttrc
```

A mail cred → password-reset interception → account takeover chain.

## Backup secrets — the offline chain

```
/root/backup.sh                    — borgpass, restic password, rclone config
/root/.config/rclone/rclone.conf   — remote creds — S3/B2 keys
/etc/duplicity/*
/root/.boto                        — gsutil/boto creds
```

`rclone.conf` → `rclone` remote access → the bucket the backups live in.

## Environment dumps — the proc chain

```
/proc/1/environ                    — dockerfile ENV — often FLAG/SECRET
/proc/self/environ                 — the app's own env
/proc/*/environ                    — every process's env
/proc/self/cmdline                 — flags may be args — --password=x
/proc/*/cmdline                    — mysql -pPASSWORD shows in cmdline!
/proc/net/tcp, tcp6                — listening services
/proc/net/arp                      — network neighbors
/proc/self/mounts                  — mounted secrets volumes
/proc/self/cgroup                  — container boundaries
```

`/proc/*/cmdline` — command-line args — `-p` passwords leak here.
`/proc/1/environ` — the container's base env — `FLAG`/`SECRET`/`KEY`
vars set in the Dockerfile.

## Cron secrets — the scheduled-task chain

```
/etc/crontab                       — system crons — scripts that run
/var/spool/cron/crontabs/root
/var/spool/cron/crontabs/*
/etc/cron.d/*
/etc/cron.hourly/* /etc/cron.daily/* /etc/cron.weekly/* /etc/cron.monthly/*
/root/*.sh                         — scripts crons call
/usr/local/bin/backup*
/opt/scripts/*.sh
```

A cron script the read can open → the script's own creds/paths →
or a writable script = the persistence path (`read-to-rce.md`).

## History-file secrets — the archaeology chain

```
/root/.bash_history                — typed commands — mysql -pPASS leaks
/home/*/.bash_history
/root/.zsh_history
/root/.mysql_history               — SELECT/INSERT show data + creds
/root/.psql_history
/root/.sqlite_history
/root/.lesshst                     — less history — files viewed
/root/.viminfo                     — vim registers — pasted secrets
/home/*/.viminfo
/root/.python_history
/root/.ipython/profile_default/history.sqlite
/root/.node_repl_history
/root/.irb_history                 — ruby
/root/.liteman_history
/root/.rediscli_history            — AUTH commands
```

`.mysql_history`/`psql_history`/`rediscli_history` — the session
artifacts carry typed commands INCLUDING `AUTH password` — the history
files are the richest secrets corpus after `.env`.

## Git secrets — the VCS chain

```
/var/www/.git/config               — remote url with embedded token
/var/www/.git-credentials
/app/.git/config
/root/.gitconfig — [credential] helper, user.email
/app/.github/workflows/*.yml
/app/.gitlab-ci.yml
/app/.gitignore                    — what SHOULD be secret
```

`.git/config` — remote URL `https://user:token@host/repo` — the token
is in the URL.

## Config-management secrets — the infra chain

```
/etc/ansible/hosts
/etc/ansible/group_vars/*
/etc/puppet/ssl/*
/etc/chef/client.pem
/etc/salt/minion_id
/etc/salt/pki/*
/var/lib/puppet/ssl/private_keys/*
```

## Web-app keystores — the java chain

```
/app/WEB-INF/classes/*.keystore
/app/WEB-INF/classes/*.jks
/app/keystore.p12
/etc/tomcat/keystore.jks
/opt/wildfly/standalone/configuration/application.keystore
```

A `.jks`/`.keystore` + the password (often in `server.xml` or
`application.properties`) → sign SAML tokens → SSO takeover.

## Session stores — the forge chain

```
/var/lib/php/sessions/sess_*
/tmp/sess_*
/var/lib/php5/sess_*
/app/tmp/sessions/*
/app/storage/framework/sessions/*  — laravel
/tmp/flask_session_*
/tmp/django_session_*
```

A session FILE read → the session's serialized contents → admin session
data → replay or forge → `../../web-deserialization/references/php-session.md`/`web-deserialization` territory.
