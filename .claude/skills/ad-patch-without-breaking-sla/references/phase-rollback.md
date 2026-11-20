# Phase: the rollback

Method module for `ad-patch-without-breaking-sla`. Close a
bug in a live scored service: bracket before/after, rollback
ready, and the four patches that cost more than they stop.

Every patch gets a one-command rollback BEFORE
applying - a patch without rollback is a bet the
service doesn't deserve.

## Exit

Named next step -> that module.
