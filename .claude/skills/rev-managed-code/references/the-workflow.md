# The managed-code workflow

1. Identify the runtime — header bytes, CLR dir, magic.
2. Inventory — dotnet_info/jclass_info --strings.
3. Locate the check — a name or a literal xref.
4. Read the deciding compare + the transform.
5. Extract the expected, invert.
6. Produce the input, verify on the real binary.
