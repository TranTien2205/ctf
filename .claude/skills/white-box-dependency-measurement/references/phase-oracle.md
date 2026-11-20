# Phase: build an oracle

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

When the source is too deep: an oracle from what
the app already leaks (error text, timing, output
diffs) - measure behavior without reading it all.

## Exit

Named next step -> that module.
