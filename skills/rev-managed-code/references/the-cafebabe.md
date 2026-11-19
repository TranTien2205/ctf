# CAFEBABE — the Java class magic

A .class file's first 4 bytes: 0xCAFEBABE — the magic. Then
minor/major version (the Java version), then the constant pool.

## The read

    xxd Main.class | head -2     # cafe babe ...
    python3 tools/jclass_info.py Main.class
