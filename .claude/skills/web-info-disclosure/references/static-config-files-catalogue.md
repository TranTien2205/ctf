# Static config file exposure — case catalogue

web.config, .htaccess, nginx.conf served inside the app, robots-style configs: the server's own ruleset as readable text.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /web.config 200 | IIS config | rewrite rules, auth rules |
| 2 | /.htaccess or /.htpasswd | Apache config/creds | rules + hashed passwords |
| 3 | /nginx.conf or site config | server rules | route map |
| 4 | /crossdomain.xml already covered | policy | see well-known |

## Falsifier

Falsifier — no server config file is served: channel closed.
