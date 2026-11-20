# Audit: credential exposure

Where the server's credentials sit: env var, config file,
hardcoded, or requested at runtime - and whether a tool
can be induced to return them into context.

## Check

The credential's storage location, the tools that can read
that location, and whether any tool's output path reaches
the model context unfiltered.

## Finding shape

A credential readable by a tool whose output is unfiltered
context is a high finding; an env-var credential unreadable
by any tool is the pass shape.

## Pivot

Module read -> the base reference files or the class boundary it names.
