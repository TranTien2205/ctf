# Patch: input filter

Method module for `ad-patch-without-breaking-sla`. Close a
bug in a live scored service: bracket before/after, rollback
ready, and the four patches that cost more than they stop.

Reject the payload shape at the boundary - cheap,
breaks when the payload varies; still the right
first patch under tick pressure.

## Exit

Named next step -> that module.
