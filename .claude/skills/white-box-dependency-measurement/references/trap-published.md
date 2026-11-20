# Trap: reasoning from docs

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

The docs describe the published release; a vendored
patch or a config flag in THIS image changes it -
measure, don't cite.

## Exit

Named next step -> that module.
