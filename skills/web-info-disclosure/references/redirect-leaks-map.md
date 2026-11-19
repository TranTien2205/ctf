# Redirect and Location-header disclosure — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Location: to an internal URL | internal route named | probe it |
| redirect chain through hidden stages | routing structure | read each hop |
| redirect body with content | body vs Location | --no-follow to read |

## Falsifier

Falsifier — redirects go straight to public pages: nothing hidden.
