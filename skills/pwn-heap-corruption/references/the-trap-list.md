# The full trap list — every way heap runs die


- wrong glibc version assumed
- tcache not drained before a fastbin/unsorted need
- key check on the second free (2.29+)
- safe-linking without a heap leak (2.32+)
- writing a raw fd where a mangled one was needed
- hooks targeted on 2.35+ (absent)
- unlink attempted post-2.30 without self-consistent links
- size forged below MINSIZE or misaligned
- the merge firing before the forge completes
- overlap assumed, marker never round-tripped
- write landed on a dead target (never fired)
- local libc used for a remote run
- alloc sizes can't express the needed classes
- OOB assumption on a bounds-checked array
- interactive clicking instead of scripted ops
