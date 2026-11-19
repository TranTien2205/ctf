# Mono — the runtime variant

A Mono-compiled binary embeds managed code differently — the
metadata layout is ECMA-335 but the loader differs; dotnet_info's
metadata walk still reads the tables when they're present.
