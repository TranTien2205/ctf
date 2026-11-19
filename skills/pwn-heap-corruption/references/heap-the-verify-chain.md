# The verify chain — every stage's check


Before composing: each stage has an independent check.

| Stage | Check |
|---|---|
| leak | value is a plausible address |
| overlap | the marker round-trips |
| poison | the two-malloc walk lands |
| write | the read-back confirms |
| redirect | the event fires |

A stage failing its check stops the composition — fix that stage.
