# Oracle: timing-channel

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

A behavior with no visible output measured by
timing - baseline first, then the distinguishing
input; report the delta in ms.

## Exit

Named next step -> that module.
