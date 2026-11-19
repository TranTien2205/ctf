# Static config file exposure — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /web.config 200 | IIS config | rewrite rules, auth rules |
| /.htaccess or /.htpasswd | Apache config/creds | rules + hashed passwords |
| /nginx.conf or site config | server rules | route map |
| /crossdomain.xml already covered | policy | see well-known |

## Falsifier

Falsifier — no server config file is served: channel closed.
