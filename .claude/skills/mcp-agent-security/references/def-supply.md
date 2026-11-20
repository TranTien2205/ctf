# Audit: supply chain

Pinned deps, no runtime downloads of extra code, no postinstall
execution, a lockfile - the server's own code is only the
visible part of its reach.

## Check

package.json/requirements for floating versions, install
scripts, and any fetch of remote code at startup.

## Finding shape

Runtime code fetch or unpinned native deps is a reject; pinned
deps with a lockfile is the pass shape.

## Pivot

Module read -> the base reference files or the class boundary it names.
