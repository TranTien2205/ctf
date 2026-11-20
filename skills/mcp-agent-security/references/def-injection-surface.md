# Audit: injection surface

Whether any tool returns open-internet or user-supplied content
into the agent's context unmarked - the injection surface's
existence is a design property, not a bug.

## Check

Each tool's return path: does fetched/page/file/record content
reach the context window, and is it marked untrusted anywhere.

## Finding shape

A tool that returns unbounded untrusted content with no marking
is a high surface; the mitigation is a marking or a boundary,
not a promise the model will behave.

## Pivot

Module read -> the base reference files or the class boundary it names.
