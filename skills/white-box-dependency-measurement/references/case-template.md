# Worked shape: a template engine

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

Pin the version, list the installed globals/
filters, try the published payload from a NEWER
version - silent failure means the gadget set
differs, not that SSTI is absent.

## Exit

Named next step -> that module.
