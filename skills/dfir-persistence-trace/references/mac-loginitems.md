# macOS: Login items / BTM

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`~/Library/Application Support/com.apple.backgroundtaskmanagementagent/BackgroundItems-v*.btm`  -  the background-item registry where modern macOS persistence shows (the file layout is UNVERIFIED here); `strings -a` on it for embedded bundle ids and paths.

## Evidence rule

Quote the plist key/value  -  `ProgramArguments` verbatim; a plist that
merely exists in LaunchAgents is a candidate until the command is read.

## Pivot

macOS quiet -> the question index (`q-*`) for the next family.
