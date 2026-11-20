# Dep type: template engines

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

Measure the sandbox: which globals, filters and
attributes the installed version exposes - a
published exploit for version N+1 fails silently
on N.

## Exit

Named next step -> that module.
