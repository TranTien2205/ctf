# The N bit — the arena marker


N (non-main-arena) in the size flags says the chunk belongs to a
thread arena — setting it on a fake/misused chunk misdirects the
free's arena computation.

## The computation

heap_info_for(chunk) uses the chunk's address bits — corrupting the
arena pointer chain is house-of-mind.

## Falsifier

The arena can't be faked in reachable memory: the bit is noise.
