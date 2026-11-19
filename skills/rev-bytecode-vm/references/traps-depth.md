# The traps — the recurring mistakes

## Wrong-version marshal

marshal.loads on a version-locked .pyc crashes or misreads — read
the magic first, match the interpreter.

## Skipped the wrong header bytes

12 vs 16 bytes — marshal.loads fails on the wrong offset.

## Decoded the table, not the program

An opcode table never applied is recon — decode the stream.

## Static-read a runtime table

A generated table isn't in the binary — trace it.

## Trusted a decompiler

Decompiled source can lie on obfuscated bytecode — dis is the
floor.

## Counted a flag-shaped const as the flag

A constant in co_consts is a CANDIDATE — verify it's the accepted
input.
