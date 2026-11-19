# The constant pool — the .class's data

The .class constant pool holds every literal and reference:
Utf8 strings, Class refs, Methodref/Fieldref — the check's expected
value and its vocabulary.

## The local tool

    python3 tools/jclass_info.py Main.class
    python3 tools/jclass_info.py Main.class --strings   # Utf8 pool

The --strings dump lists the Utf8 entries — flag-shaped constants
surface before reading instructions.
