# The chain's layout — the qword map


    [padding × offset]
    [pop gadget]          ← saved rip slot
    [arg value]
    [next gadget]
    [arg value]
    [alignment ret]?      ← if needed
    [call target]
    [ending]

Each ret consumes one qword — rsp walks the chain top to bottom.
