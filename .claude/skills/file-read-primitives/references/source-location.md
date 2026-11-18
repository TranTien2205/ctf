# Source Location — finding the app's own files

## The "find the app" problem — you don't know where the code is

The read works — now locate the app's own source — the read that names
the flag's location.

## The `/proc/self/*` recon — the process reveals itself

```
/proc/self/cmdline       — the entrypoint — /usr/bin/python3 /app/main.py
/proc/self/environ       — PWD, DOCUMENT_ROOT, APP_DIR, env-vars
/proc/self/cwd           — the working dir — /app
/proc/self/exe           — the interpreter — /usr/bin/python3
/proc/self/maps          — mapped libs
/proc/self/mountinfo     — bind-mounts — the host-paths
/proc/self/status        — Uid/Gid — the user
```

`cmdline` names the script → `cwd` names the dir → `environ` names the
env — the app-location triad.

## The "the interpreter names the stack" — per-stack app paths

### PHP

```
/var/www/html/index.php
/var/www/html/config.php
/var/www/html/app.php
/var/www/html/wp-config.php
/var/www/html/.env
/var/www/html/composer.json
/var/www/html/vendor/
/var/www/index.php
/srv/www/htdocs/index.php
/usr/share/nginx/html/index.php
/usr/local/apache2/htdocs/index.php
```

### Python

```
/app/main.py
/app/app.py
/app/wsgi.py
/app/asgi.py
/app/server.py
/app/config.py
/app/settings.py
/app/routes.py
/app/__init__.py
/app/requirements.txt
/app/Pipfile
/app/.env
/usr/src/app/main.py
/usr/src/app/app.py
/opt/app/main.py
/home/app/main.py
/home/ctf/app.py
/home/ctf/main.py
```

### Node

```
/app/server.js
/app/index.js
/app/app.js
/app/main.js
/app/routes/*.js
/app/package.json
/app/package-lock.json
/app/.env
/app/node_modules/
/usr/src/app/server.js
/opt/app/server.js
/home/app/server.js
/home/ctf/app.js
```

### Java

```
/app/WEB-INF/web.xml
/app/WEB-INF/applicationContext.xml
/app/WEB-INF/classes/application.properties
/app/WEB-INF/classes/application.yml
/app/WEB-INF/classes/config.yml
/app/WEB-INF/classes/*.properties
/app/WEB-INF/classes/META-INF/persistence.xml
/app/WEB-INF/classes/META-INF/MANIFEST.MF
/app/WEB-INF/lib/*.jar
/app/pom.xml
/app/build.gradle
/app/src/main/resources/application.properties
/app/src/main/resources/application.yml
/app/src/main/java/**/*.java
/opt/tomcat/webapps/ROOT/WEB-INF/web.xml
/opt/tomcat/webapps/ROOT/WEB-INF/classes/application.properties
/usr/share/tomcat/webapps/*/WEB-INF/web.xml
/var/lib/tomcat*/webapps/*/WEB-INF/web.xml
/opt/jboss/standalone/deployments/*.war
/opt/wildfly/standalone/deployments/*.war
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.war!/WEB-INF/classes/application.properties
```

### Ruby

```
/app/config/routes.rb
/app/config/database.yml
/app/config/secrets.yml
/app/config/application.rb
/app/config/environment.rb
/app/config/environments/production.rb
/app/config/initializers/*.rb
/app/Gemfile
/app/Gemfile.lock
/app/.env
/app/app/controllers/*.rb
/app/app/models/*.rb
/srv/www/*/config/routes.rb
```

### Go

```
/app/main.go
/app/go.mod
/app/go.sum
/app/config.yaml
/app/.env
/usr/src/app/main.go
```

### .NET

```
/app/web.config
/app/appsettings.json
/app/appsettings.Production.json
/app/*.dll
/app/*.exe
/app/bin/*.dll
C:\inetpub\wwwroot\web.config
C:\inetpub\wwwroot\appsettings.json
C:\inetpub\wwwroot\bin\*.dll
```

## The "the server config names the docroot" — reverse-lookup

```
/etc/nginx/nginx.conf          — server { root /var/www/html; }
/etc/nginx/sites-enabled/*
/etc/apache2/sites-enabled/*
/etc/apache2/apache2.conf
/etc/httpd/conf/httpd.conf
/etc/httpd/conf.d/*.conf
/etc/lighttpd/lighttpd.conf
/etc/caddy/Caddyfile
/etc/haproxy/haproxy.cfg
/etc/tomcat*/server.xml
/opt/tomcat/conf/server.xml
```

The web-server config NAMES the docroot — read the config → find the
app dir → read the source.

## The "the entry-point names the source" — `cmdline`-driven

`/proc/self/cmdline` = `python3 /app/main.py` → read `/app/main.py` →
see `from config import FLAG` → read `/app/config.py` → the flag —
the include-chain drives the read-list.

## The "the source imports the next file" — the include-chain

```
index.php → require 'config.php' → read config.php → require '/opt/secret/db.php' → read it
```

Each source-read names the next — the include-chain is the read-
navigation engine.

## The "the framework's config names the secrets" — the config-read

```
config/database.yml     — DB creds
config/secrets.yml      — secret-key
.env                    — APP_KEY, DB_*, FLAG
application.properties   — spring properties
web.config              — .NET config
appsettings.json        — .NET settings
config.yaml             — generic yaml
settings.py             — django
local_settings.py       — django local
wp-config.php           — wordpress
configuration.php        — joomla
```

## The "the vendor/dependency lists the lib versions" — the dep-read

```
composer.json / composer.lock      — PHP deps → gadget_lookup
package.json / package-lock.json   — Node deps
requirements.txt / Pipfile.lock    — Python deps
pom.xml / build.gradle             — Java deps
Gemfile / Gemfile.lock             — Ruby deps
go.mod / go.sum                    — Go deps
Cargo.toml / Cargo.lock            — Rust deps
```

The dep-list → `tools/gadget_lookup.py --lockfile` — the version-aware
vuln lookup.

## The "the .env is the flag" — the `.env`-read

`.env` carries `FLAG=...`/`APP_KEY`/`DB_PASSWORD`/`SECRET`/`JWT_SECRET`/
`SESSION_SECRET` — the most-common single secret-file — try `.env`,
`.env.local`, `.env.production`, `.env.docker`, `.env.dev`, `.env.prod`.
