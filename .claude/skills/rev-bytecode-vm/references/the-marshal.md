# marshal — the code object


marshal.loads returns the module's code object — co_code is the
bytecode, co_consts the constants, co_names the names, co_consts
nests function code objects.

## The walk

    import marshal, dis
    code = marshal.loads(open('x.pyc','rb').read()[16:])
    dis.dis(code)
    for c in code.co_consts:
        if hasattr(c, 'co_code'): dis.dis(c)   # nested functions
