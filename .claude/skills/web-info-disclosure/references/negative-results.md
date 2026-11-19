# Negative results — recording closed channels

A channel that produced nothing is a measurement, recorded with the probe that closed it.

## The recording

Per channel: what was probed, what was observed (the baseline-diff or the falsifier firing), and what would reopen it (new evidence naming a path).

| Channel | Negative | Reopens if |
|---|---|---|
| .git | HEAD not 'ref:' or all-404 | evidence names a VCS path |
| config | catch-all on all names | a hint names a custom name |
| archives | all-404, no hints | a listing shows a zip |
| debug | generic errors everywhere | a debug header appears |
| source-maps | no maps | a map link surfaces |

Record in `../field-notes.md`. A channel closed by its own falsifier is done — not a retry candidate.

## Falsifier

--

## Cross-references

`falsifiers.md`
