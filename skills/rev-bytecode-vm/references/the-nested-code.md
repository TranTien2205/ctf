# Nested code objects — co_consts walk


Functions are code objects inside co_consts — recurse:

    def walk(c, depth=0):
        dis.dis(c)
        for x in c.co_consts:
            if hasattr(x,'co_code'): walk(x, depth+1)

## The target

The check usually lives in a nested function (check/verify/main).
