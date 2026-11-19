# r2pipe — scripting r2


r2pipe is Python's r2 bridge — if importable:

    import r2pipe
    r = r2pipe.open('./chal')
    r.cmd('aaa')
    funcs = r.cmdj('aflj')

Check availability — a scripting surface for the repetitive reads.
