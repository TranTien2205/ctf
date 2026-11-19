# ilspycmd — the .NET decompiler

ILSpy's CLI — `ilspycmd app.exe` decompiles to C# — the readable
source form. Absent on this box? dotnet_info's metadata walk + a
manual IL read is the floor.

## What it gives

The C# view of each method — the check's logic in high-level form:
`if (input == expected) ...` readable directly.
