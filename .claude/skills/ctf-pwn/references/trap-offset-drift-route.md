# Route card: trap-offset-drift

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Companion to `trap-offset-drift.md`.

## When to open the base

When the protection story or the question lands on this topic - the
base module carries the technique detail; this card only carries
the routing decision.

## Inputs it needs

The triage output (protections, imports, arch) and the question
shape. If the artifact the base names is absent, the topic is
'not checkable' - not 'absent'.

## Outputs it feeds

A named primitive with its precondition, or a recorded negative
pointing at the next technique file.

## Neighbours

The class skills it feeds: pwn-stack-overflow, pwn-format-string,
pwn-heap-corruption, pwn-code-reuse, pwn-rop.
