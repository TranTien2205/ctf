# macOS: LaunchDaemons / LaunchAgents

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/Library/LaunchDaemons/*.plist` (root, at boot), `/Library/LaunchAgents` (all users, at login), `~/Library/LaunchAgents` (one user), `/System/Library/Launch{Agents,Daemons}` (Apple-owned  -  a foreign file there is loud). Keys: `Label`, `ProgramArguments` (the command), `RunAtLoad`, `StartInterval` (T1543.001). `plistlib` reads it: `python3 -c "import plistlib,sys;print(plistlib.load(open(sys.argv[1],'rb')))" <f>.plist`.

## Evidence rule

Quote the plist key/value  -  `ProgramArguments` verbatim; a plist that
merely exists in LaunchAgents is a candidate until the command is read.

## Pivot

macOS quiet -> the question index (`q-*`) for the next family.
