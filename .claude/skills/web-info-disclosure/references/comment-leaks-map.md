# HTML and code comments — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| <!-- TODO/FIXME/admin in page source | comment leak | read all comments |
| Internal URLs in comments | route disclosure | probe them |
| Credentials or test values in comments | secret leak | test or note |
| <!-- flag{ or challenge hints | intended breadcrumb | follow |

## Falsifier

Falsifier — pages carry no comments beyond framework boilerplate: nothing disclosed.
