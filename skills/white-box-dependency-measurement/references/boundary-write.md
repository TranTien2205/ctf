# Writing boundary statements

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

shape: 'X holds when <measurable condition>;
measured by <probe> on <version>' - a negative
result gets the same statement form.

## Exit

Named next step -> that module.
