# Deep dive: Deep: the userinit trailing comma

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Default `Userinit` = `C:\Windows\system32\userinit.exe,`  -  the trailing comma IS the stock value (it separates the binary from appended args). `userinit.exe,C:\bad.exe,` = appended persistence; `userinit.exe` with no comma is itself anomalous (rewritten value).

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.
