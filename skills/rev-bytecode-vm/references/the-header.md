# The .pyc header — 12 or 16 bytes


The header: magic(4) + bit-field(4) + mtime/hash(4) + size(4) — 16
bytes on 3.7+; 12 bytes on older. marshal.loads on the wrong offset
fails before the code object parses.

## The rule

    d = open('x.pyc','rb').read()
    code = marshal.loads(d[16:])   # 3.7+
    # or d[12:] for older versions
