# Calling twice — multi-call chains


A chain can call several functions in sequence — each call's "return
address" is the next call's entry.

## The shape

    [pop rdi][arg][func1][pop rdi][arg][func2]...

func1's return address is the next qword — it continues the chain.

## The use

- leak func + restart func in one chain.
- write() then read() then system() — a multi-op payload.

## Falsifier

A function clobbers state the next call needs: sequence them so the
destructive call comes last.
