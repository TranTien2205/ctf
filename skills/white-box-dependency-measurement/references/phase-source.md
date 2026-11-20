# Phase: read the installed source

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

node_modules/<pkg>/ in the container, the vendored
tree, or the base image's package - the code that
actually runs.

## Exit

Named next step -> that module.
