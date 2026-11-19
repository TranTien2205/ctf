# Directory listing — autoindex and open dirs — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /uploads/ or /files/ returns an index page | autoindex on | read every entry |
| 'Index of /' in the body | nginx/Apache autoindex | walk subdirs |
| Parent Directory link | traversable listing | walk up and sideways |
| A dir 403s on GET / but indexes on a subdir | partial exposure | probe siblings |

## Falsifier

Falsifier — every directory path returns the catch-all or 403 with no index body: autoindex is off. Filenames would have to be guessed, which is out of scope unless hinted.
