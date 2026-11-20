# gadget_lookup in the flow

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

lockfile -> gadget_lookup --lockfile -> known
measured gadgets; a miss means measure yourself,
not 'no gadget exists'.

## Exit

Named next step -> that module.
