# Single-file .NET bundles

A self-contained .NET 5+ exe bundles the assemblies inside — the
app.dll is embedded; extract it before the decompiler sees real
code.

## The extract

The bundle's manifest lists embedded assemblies — carve app.dll
out, then dotnet_info on it.
