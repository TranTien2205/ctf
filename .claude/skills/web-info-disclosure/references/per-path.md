# Per-path map — the canonical list with the file that owns each

| Path | Positive shape | Owner |
|---|---|---|
| /.git/HEAD | 'ref: refs/heads/...' | `git-exposure.md` |
| /.git/config | remote/object db | `git-exposure.md` |
| /.svn/entries or wc.db | SVN metadata | `version-control-metadata.md` |
| /.hg/requires | HG metadata | `version-control-metadata.md` |
| /.env /.env.bak /.env.old /.env.local | KEY=VALUE | `env-config-leaks.md` |
| /config.json /config.yml /settings.py | structured config | `env-config-leaks.md` |
| /backup.zip /app.zip /site.tar.gz | archive magic | `backup-archives.md` |
| /db.sql /dump.sql /backup.sql | SQL text | `sql-dump-read.md` |
| /index.php~ /index.php.bak /.index.php.swp | source text | `swp-and-temp.md` |
| /composer.json /package.json /requirements.txt /Gemfile.lock /go.sum | manifest | `manifest-files.md` |
| /web.config /.htaccess /.htpasswd /nginx.conf | server rules | `static-config-files.md` |
| /id_rsa /.ssh/id_rsa /server.key /key.pem | private key | `pem-key-files.md` |
| /.DS_Store /Thumbs.db | binary dir metadata | `ds-store-parse.md` |
| /robots.txt /sitemap.xml | Disallow/URL list | `robots-sitemap.md` |
| /server-status /nginx_status /phpinfo.php /metrics /health | ops surface | `status-pages.md` |
| /access.log /error.log /logs/ /debug.log | log content | `log-exposure.md` |
| /actuator /actuator/env /actuator/mappings /actuator/heapdump | Spring ops | `spring-actuator-deep.md` |
| /console /__debug__/ /_profiler /telescope | framework debug | `framework-debug.md` |
| /swagger.json /openapi.json /api-docs /graphql | API spec | `api-docs-exposure.md` |
| /security.txt /crossdomain.xml /.well-known/openid-configuration | meta/policy | `well-known-and-meta.md` |
| /.idea/ /.vscode/ /.gitlab-ci.yml /docker-compose.yml /Dockerfile | build config | `ide-and-ci-files.md` |
| /uploads/ /files/ /backup/ /static/ | index page | `directory-listing.md` |
