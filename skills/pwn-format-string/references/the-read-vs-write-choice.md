# Read vs write — the branch in the primitive


The format primitive splits into two uses: the READ (%p/%x/%s) leaks
values; the WRITE (%n/%hn/%hhn) redirects execution.

## Choose by need

- Need a value (canary, base, address)? → read.
- Need to redirect execution? → write.
- Often both: the read feeds the write's value/target.

## The composition

The read supplies the leaked values; the write redirects — the standard
two-stage.
