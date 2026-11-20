# Phase: identify the installed

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

package-lock/go.sum/pip-freeze inside the image -
the PINNED version, not the range in package.json.

## Exit

Named next step -> that module.
