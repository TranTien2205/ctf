# Phase: the bracket

Method module for `ad-patch-without-breaking-sla`. Close a
bug in a live scored service: bracket before/after, rollback
ready, and the four patches that cost more than they stop.

sla_check before the patch -> patch -> sla_check
after. --compare refuses a patch that broke a
previously-passing check, including renamed or
deleted checks.

## Exit

Named next step -> that module.
