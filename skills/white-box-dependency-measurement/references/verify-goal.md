# The verify goal

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

A chain whose every dependency assumption is a
measured number can be committed to; one resting
on 'should behave like' cannot.

## Exit

Named next step -> that module.
