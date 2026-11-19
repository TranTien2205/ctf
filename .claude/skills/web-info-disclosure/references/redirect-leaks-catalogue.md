# Redirect and Location-header disclosure — case catalogue

302s leak internal URLs; redirect chains reveal routing structure and sometimes unauthenticated intermediate content.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Location: to an internal URL | internal route named | probe it |
| 2 | redirect chain through hidden stages | routing structure | read each hop |
| 3 | redirect body with content | body vs Location | --no-follow to read |

## Falsifier

Falsifier — redirects go straight to public pages: nothing hidden.
