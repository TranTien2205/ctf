# Negative: docs are enough

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

When the behavior is a documented, version-stable
constant - skip measuring; the method exists for
behavior that drifts.

## Exit

Named next step -> that module.
