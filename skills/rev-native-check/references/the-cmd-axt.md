# axt deep — xref variants


    axt @ addr        # xrefs TO
    axf @ addr        # xrefs FROM
    axg @ addr        # the xref graph
    axtj @ addr       # JSON

The to/from pair walks both directions — data xrefs (axt) find the
string readers; code xrefs (axt on a call's target) find the callers.
