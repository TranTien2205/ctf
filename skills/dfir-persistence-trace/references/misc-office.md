# Persistence misc: Office add-ins and templates

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`%APPDATA%\Microsoft\Word\STARTUP\*.wll` (T1137.006), `%APPDATA%\Microsoft\Excel\XLSTART\*.xll`/`*.xlam`, `%APPDATA%\Microsoft\Templates\Normal.dotm`  -  template persistence fires when the document opens. `olefile` imports here (`oletools` absent): `python3 -c "import olefile,sys;print(olefile.OleFileIO(sys.argv[1]).listdir())"`.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
