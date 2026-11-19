# TypeDef and MethodDef — the .NET map

The #~ table's TypeDefs name every class (namespace.name);
MethodDefs name every method with its RVA — the check function is
a MethodDef.

## The locate

    python3 tools/dotnet_info.py app.exe
    # TypeDefs: App.Checker, App.Verify ...
    # MethodDefs: CheckFlag, Verify, Compare ...

Names usually survive unobfuscated metadata — the check's name
jumps out before decompiling.
