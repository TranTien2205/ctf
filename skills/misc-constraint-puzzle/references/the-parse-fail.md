# Parse failures — log and skip

An unparseable line might be filler — log it and keep buffering;
crashing on a non-question line kills the run.

## Skip fillers

Unparseable != crash — log and keep buffering.

## Skip

Unparseable line -> log, keep buffering.
