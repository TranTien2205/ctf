# argv/env — another pointer surface


argv and envp are stack-top pointers the process exposes — a leaked
stack region contains them; they also hold planted strings.

## Use

- A leaked argv pointer names a stack address.
- An env var carrying your string = a planted "read" target.

## Falsifier

No stack leak: the pointers are unknowable.
