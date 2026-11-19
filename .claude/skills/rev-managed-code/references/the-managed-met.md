# Managed vs native — the stub boundary

A .NET assembly has real managed code; a thin native launcher
doesn't. The CLR directory's size + the TypeDef count tell whether
the logic is managed.

## The boundary

Empty CLR dir or a single native stub → rev-native-check.
