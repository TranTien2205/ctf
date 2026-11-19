# The #US heap — where the literals live

Every `ldstr "..."` in the IL reads a #US-heap string — the
check's expected values, the flag format, the error strings sit
here.

## The dump

    python3 tools/dotnet_info.py app.exe --strings

A flag-shaped or suspicious literal here is a candidate — verify
it's the accepted input.
