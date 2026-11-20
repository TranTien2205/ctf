# Measurement: exact version

Method module for `white-box-dependency-measurement`.
Measure the INSTALLED dependency: the pinned version, the
vendored patch, the actual container behavior - never the
published docs. Every boundary is stated as a number.

lockfile > package.json range > 'about the same'.
docker exec `pip show` / `npm ls` inside the real
container is the final word.

## Exit

Named next step -> that module.
