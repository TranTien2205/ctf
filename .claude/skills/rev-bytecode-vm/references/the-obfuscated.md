# Obfuscated bytecode — dead code and tricks

## Dead code

Bytes never executed — decode only reaches them if pc walks there;
skip them by tracing real pc flow.

## Opaque predicates

Jumps that always go one way — the branch is fake; follow the real
target.

## Weird ops

An opcode that does nothing meaningful (nop variants) — ignore.

## The rule

Decode the EXECUTED stream, not the raw bytes — trace, or follow
the jumps.
