# Response anatomy — what each status really means — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| 200 with the app's shell for every path | catch-all | content-diff, not status |
| 403 on a path that then 404s a sibling | exists-but-forbidden vs absent | verb/host tricks |
| 301/302 to a real location | route exists elsewhere | follow or note the target |
| 401 vs 403 | auth-required vs forbidden | auth class boundary |

## Falsifier

Falsifier — every probed path returns the identical catch-all body: nothing in the bounded list is exposed. Wider fuzzing is out of scope for this class.
