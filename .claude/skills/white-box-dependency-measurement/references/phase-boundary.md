# Phase: state boundaries numerically

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

'Long' is not a boundary; 'more than 4096 bytes
truncates' is. Every claim carries the number and
how it was measured.

## Exit

Named next step -> that module.
