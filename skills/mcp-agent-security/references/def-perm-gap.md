# Audit: permission-vs-purpose gap

The declared purpose vs the requested scope - a doc-search tool
asking for shell exec is the finding shape. The gap itself is the
reportable item.

## Check

Read the manifest's declared purpose, then the permission set
each tool requests; any permission not load-bearing for the
purpose is the gap.

## Finding shape

List each over-requested permission with the purpose it fails
to serve.

## Pivot

Module read -> the base reference files or the class boundary it names.
