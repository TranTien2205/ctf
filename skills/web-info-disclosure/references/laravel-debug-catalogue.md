# Laravel Ignition/Whoops — PHP debug pages — case catalogue

Laravel's Ignition (or older Whoops) page dumps env vars, request data, and the full stack — plus a known RCE in old Ignition.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Ignition-styled error page | debug on | env vars in page |
| 2 | APP_KEY visible | encryption key | decrypt/forge data |
| 3 | env section | all env vars | secrets harvest |
| 4 | solution cards / execute button | interactive fix | RCE boundary |

## Falsifier

Falsifier — standard Laravel error page or plain 500: debug off.
